# -*- coding: utf-8 -*-
import io
import json
import os
import re
from datetime import datetime
from decimal import Decimal
from xml.sax.saxutils import escape
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from django.conf import settings
from storage_control.models import PurchaseRequest, WarehouseTmc

# Справочник кодов ОКЕИ для прямого обмена с 1С:Бухгалтерия / 1С:УТ / 1С:ERP
OKEI_MAP = {
    "шт": ("796", "шт"),
    "шт.": ("796", "шт"),
    "компл": ("839", "компл"),
    "компл.": ("839", "компл"),
    "м": ("006", "м"),
    "пог. м": ("006", "м"),
    "м2": ("055", "м2"),
    "м²": ("055", "м2"),
    "м3": ("113", "м3"),
    "м³": ("113", "м3"),
    "кг": ("166", "кг"),
    "т": ("168", "т"),
    "упак": ("778", "упак"),
    "л": ("112", "л"),
}


def normalize_okei(unit_raw: str) -> tuple[str, str]:
    """Возвращает пару (код_ОКЕИ_для_1С, стандартное_обозначение)."""
    u = (unit_raw or "шт").strip().lower()
    return OKEI_MAP.get(u, ("796", "шт"))


def extract_1c_document_payload(vision_result: dict) -> dict:
    """
    Шаги 4–5: Превращает сырой результат «Зрения сокола» (OCR + QR ФНС + штрихкоды)
    в структурированный пакет реквизитов для Склада, Реестра ИД и 1С.
    """
    ocr_text = vision_result.get("ocr_preview", "") or ""
    codes = vision_result.get("codes_found", []) or []
    doc_kind = vision_result.get("doc_kind", "UPD_INVOICE")

    qr_parsed = {}
    for c in codes:
        if c.get("parsed"):
            qr_parsed.update(c["parsed"])

    m_inn = re.search(r'(?:инн|inn)[\s:№]*(\d{10}|\d{12})\b', ocr_text, re.IGNORECASE)
    inn = qr_parsed.get("inn") or (m_inn.group(1) if m_inn else "")

    m_doc = re.search(r'(?:упд|накладная|счет-фактура|паспорт|сертификат)\s*[№#]?\s*([А-ЯЁA-Z0-9\-/]{1,25})', ocr_text, re.IGNORECASE)
    doc_number = qr_parsed.get("doc_num") or (m_doc.group(1) if m_doc else "")

    m_date = re.search(r'\b(\d{2}\.\d{2}\.\d{4})\b', ocr_text)
    doc_date = qr_parsed.get("date") or (m_date.group(1) if m_date else "")

    m_sum = re.search(r'(?:итого|всего\s+к\s+оплате|сумма)[^\d]{0,20}(\d[\d\s]{0,12}[\.,]\d{2})', ocr_text, re.IGNORECASE)
    total_sum = qr_parsed.get("sum") or (m_sum.group(1).replace(" ", "").replace(",", ".") if m_sum else "")

    extracted_lines = []
    line_pattern = re.compile(
        r'([А-ЯЁA-Z][А-ЯЁA-Zа-яёa-z0-9\s\-\.,"/\(\)х×]{5,90}?)\s+(\d+(?:[\.,]\d+)?)\s*(шт\.?|компл\.?|пог\.?\s*м|м2|м²|м3|м³|м|кг|т|упак|л)\b',
        re.IGNORECASE,
    )

    for ln in ocr_text.splitlines():
        m_item = line_pattern.search(ln.strip())
        if not m_item:
            continue
        raw_title = re.sub(r'\s+', ' ', m_item.group(1)).strip(" -–.,")
        if len(raw_title) < 5 or any(skip in raw_title.lower() for skip in ("итого", "всего", "инн", "кпп", "адрес")):
            continue
        qty_val = Decimal(m_item.group(2).replace(",", "."))
        okei_code, okei_name = normalize_okei(m_item.group(3))

        token = next(iter(raw_title.lower().split()), "")
        rd_match = PurchaseRequest.objects.filter(material_name__icontains=token).first() if len(token) >= 4 else None

        extracted_lines.append({
            "photo_material_name": raw_title,
            "incoming_qty": float(qty_val),
            "unit": okei_name,
            "okei_code_1c": okei_code,
            "matched_rd_name": rd_match.material_name if rd_match else "⚠️ Новая позиция (нет в РД)",
            "rd_planned_qty": float(rd_match.required_qty) if rd_match else 0.0,
            "rd_doc_title": rd_match.document.title if (rd_match and rd_match.document) else "",
        })

    if doc_kind == "UPD_INVOICE":
        target_1c_doc = "Поступление товаров и услуг (УПД / Приходный ордер М-4)"
    elif doc_kind == "QUALITY_CERT":
        target_1c_doc = "Прикрепление сертификата качества в ИД и карточку партии 1С"
    else:
        target_1c_doc = "Складская идентификация партии / маркировка"

    return {
        "target_1c_doc": target_1c_doc,
        "supplier_inn": inn,
        "doc_number": doc_number,
        "doc_date": doc_date,
        "total_sum": total_sum,
        "detected_axes": vision_result.get("detected_axes", ""),
        "detected_elevation": vision_result.get("detected_elevation", ""),
        "items": extracted_lines,
        "ready_for_1c": bool(extracted_lines or inn or doc_number),
    }


def commit_1c_intake_to_warehouse_and_log(payload: dict, operator: str = "ПТО Штаб") -> dict:
    """
    Шаги 6–7: Проводит приёмку позиций из УПД/паспорта на склад WarehouseTmc,
    уменьшает дефицит по заявкам РД и записывает событие в журнал аудита «Тритон & Жук».
    """
    accepted = []
    doc_num = payload.get("doc_number") or "Б/Н"
    doc_date = payload.get("doc_date") or datetime.now().strftime("%d.%m.%Y")
    inn = payload.get("supplier_inn") or ""

    for it in payload.get("items", []):
        title = it["photo_material_name"]
        qty = Decimal(str(it["incoming_qty"]))
        unit = it["unit"]

            for it in payload.get("items", []):
        title = it["photo_material_name"]
        qty = Decimal(str(it["incoming_qty"]))
        unit = it["unit"]

        auto_code = f"1C-{abs(hash(title)) % 900000 + 100000}"
        wh_obj, _ = WarehouseTmc.objects.get_or_create(
            nomenclature=title,
            defaults={"item_code": auto_code, "unit": unit, "stock_balance": Decimal("0")},
        )
        wh_obj.stock_balance = (wh_obj.stock_balance or Decimal("0")) + qty


        wh_obj, _ = WarehouseTmc.objects.get_or_create(
            nomenclature=title,
            defaults={"unit": unit, "stock_balance": Decimal("0")},
        )
        wh_obj.stock_balance = (wh_obj.stock_balance or Decimal("0")) + qty
        if hasattr(wh_obj, "certificate_number") and not wh_obj.certificate_number:
            wh_obj.certificate_number = f"УПД №{doc_num} от {doc_date}"
        wh_obj.save()

        token = next(iter(title.lower().split()), "")
        req = PurchaseRequest.objects.filter(material_name__icontains=token, deficit_qty__gt=0).first() if len(token) >= 4 else None
        reduced_deficit = Decimal("0")
        if req:
            reduced_deficit = min(req.deficit_qty, qty)
            req.deficit_qty = max(Decimal("0"), req.deficit_qty - reduced_deficit)
            req.save()

        accepted.append({
            "nomenclature": title,
            "added_qty": float(qty),
            "new_stock_balance": float(wh_obj.stock_balance),
            "unit": unit,
            "okei_code_1c": it.get("okei_code_1c", "796"),
            "deficit_reduced": float(reduced_deficit),
        })

    log_dir = os.path.join(settings.BASE_DIR, "media", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "triton_juk_events.jsonl")
    event_record = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "guardian": "Triton & Juk Audit Engine",
        "operator": operator,
        "target_1c_doc": payload.get("target_1c_doc", ""),
        "supplier_inn": inn,
        "doc_number": doc_num,
        "doc_date": doc_date,
        "axes": payload.get("detected_axes", ""),
        "elevation": payload.get("detected_elevation", ""),
        "accepted_count": len(accepted),
        "items": accepted,
    }
    with open(log_path, "a", encoding="utf-8") as lf:
        lf.write(json.dumps(event_record, ensure_ascii=False) + "\n")

    return {"ok": True, "accepted_items": accepted, "log_file": log_path}


def build_1c_exchange_files(payload: dict) -> tuple[bytes, bytes]:
    """
    Шаги 8–9: Генерирует два готовых файла обмена с 1С:
    1) Excel-шаблон загрузки документа в 1С (.xlsx);
    2) Стандартный XML-файл КоммерческаяИнформация 2.10 (.xml) для 1С:УТ / 1С:Бухгалтерия / 1С:ERP.
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Загрузка_1С_Приход"

    headers = (
        "ВидДокумента1С", "НомерДокумента", "ДатаДокумента", "ИНН_Поставщика",
        "Номенклатура", "КодОКЕИ", "ЕдИзм", "Количество", "СуммаДокумента", "Оси_Зона_Объекта"
    )
    ws.append(list(headers))
    fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
    font = Font(name="Calibri", size=11, bold=True, color="38BDF8")
    for idx in range(1, len(headers) + 1):
        c = ws.cell(row=1, column=idx)
        c.fill = fill
        c.font = font
        c.alignment = Alignment(horizontal="center", vertical="center")
        ws.column_dimensions[openpyxl.utils.get_column_letter(idx)].width = 22

    doc_type = payload.get("target_1c_doc", "Поступление товаров (УПД)")
    doc_num = payload.get("doc_number", "")
    doc_date = payload.get("doc_date", "")
    inn = payload.get("supplier_inn", "")
    total_sum = payload.get("total_sum", "")
    zone = f"{payload.get('detected_axes', '')} {payload.get('detected_elevation', '')}".strip()

    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<КоммерческаяИнформация ВерсияСхемы="2.10" ДатаФормирования="' + datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + '">',
        '  <Документ>',
        f'    <ХозОперация>{escape(doc_type)}</ХозОперация>',
        f'    <Номер>{escape(str(doc_num))}</Номер>',
        f'    <Дата>{escape(str(doc_date))}</Дата>',
        f'    <ИННПоставщика>{escape(str(inn))}</ИННПоставщика>',
        f'    <Сумма>{escape(str(total_sum))}</Сумма>',
        f'    <Комментарий>{escape(zone)}</Комментарий>',
        '    <Товары>',
    ]

    for it in payload.get("items", []):
        ws.append([
            doc_type, doc_num, doc_date, inn,
            it["photo_material_name"], it.get("okei_code_1c", "796"),
            it["unit"], it["incoming_qty"], total_sum, zone
        ])
        xml_lines.extend([
            '      <Товар>',
            f'        <Наименование>{escape(it["photo_material_name"])}</Наименование>',
            f'        <БазоваяЕдиница Код="{escape(it.get("okei_code_1c", "796"))}">{escape(it["unit"])}</БазоваяЕдиница>',
            f'        <Количество>{it["incoming_qty"]}</Количество>',
            '      </Товар>',
        ])

    xml_lines.extend(['    </Товары>', '  </Документ>', '</КоммерческаяИнформация>'])

    xlsx_buf = io.BytesIO()
    wb.save(xlsx_buf)
    return xlsx_buf.getvalue(), "\n".join(xml_lines).encode("utf-8")
