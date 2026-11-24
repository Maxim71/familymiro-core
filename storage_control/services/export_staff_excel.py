# -*- coding: utf-8 -*-
import io
from decimal import Decimal
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from storage_control.models import PurchaseRequest, BimCrossLink
from storage_control.services.route_tracer import build_engineering_procurement_rows

HEADER_FILL = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
HEADER_FONT = Font(name="Calibri", size=11, bold=True, color="FFD700")
TOTAL_FILL = PatternFill(start_color="E2E8F0", end_color="E2E8F0", fill_type="solid")
TOTAL_FONT = Font(name="Calibri", size=11, bold=True, color="0F172A")
LINK_FONT = Font(name="Calibri", size=10, underline="single", color="0284C7")
THIN_BORDER = Border(
    left=Side(style="thin", color="CBD5E1"),
    right=Side(style="thin", color="CBD5E1"),
    top=Side(style="thin", color="CBD5E1"),
    bottom=Side(style="thin", color="CBD5E1"),
)


def _style_header(ws, headers, widths):
    ws.append(list(headers))
    for col_idx, width in enumerate(widths, start=1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = THIN_BORDER
        col_letter = openpyxl.utils.get_column_letter(col_idx)
        ws.column_dimensions[col_letter].width = width
    ws.row_dimensions.height = 28
    ws.freeze_panes = "A2"


def build_staff_excel_bytes(doc=None) -> bytes:
    """Формирует очищенный штабной Excel (.xlsx) из 3 листов с инженерной группировкой."""
    wb = openpyxl.Workbook()

    qs = PurchaseRequest.objects.select_related("document").order_by("discipline", "room_info", "id")
    if doc is not None:
        qs = qs.filter(document=doc)
    raw_items = list(qs)
    clean_rows = build_engineering_procurement_rows(raw_items)

    # --- ЛИСТ 1: СНАБЖЕНИЕ (ОЧИЩЕННАЯ СВОДНАЯ ВЕДОМОСТЬ) ---
    ws_buy = wb.active
    ws_buy.title = "1. Снабжение (Закупки)"
    buy_headers = (
        "№", "Помещение / Отметка", "Группа снабжения", "Чистое наименование ТМЦ",
        "Ед. изм.", "По проекту", "На складе", "К закупке (Дефицит)",
        "Кратность поставки", "Срок и звено (ЕНиР)", "BIM / Поставщик", "Ответственный"
    )
    buy_widths = (5, 20, 26, 40, 10, 14, 13, 16, 26, 28, 32, 18)
    _style_header(ws_buy, buy_headers, buy_widths)

    buy_rows = [r for r in clean_rows if r["record_type"] == "BUY"]
    total_req = Decimal("0")
    total_def = Decimal("0")

    for idx, r in enumerate(buy_rows, start=1):
        req_v = Decimal(str(r["required_qty"]))
        stk_v = Decimal(str(r["stock_qty"]))
        def_v = Decimal(str(r["deficit_qty"]))
        total_req += req_v
        total_def += def_v
        bim_or_vendor = r["bim_badge"] or r["vendor_badge"] or "По проекту РД"

        ws_buy.append([
            idx,
            r["location"],
            r["node_cabinet"],
            r["material_name"],
            r["unit"],
            float(req_v),
            float(stk_v),
            float(def_v),
            r["pack_hint"] or "Стандартная поставка",
            r["schedule_hint"],
            bim_or_vendor,
            r["assigned_itr"],
        ])
        r_num = ws_buy.max_row
        for c in range(1, 13):
            cell = ws_buy.cell(row=r_num, column=c)
            cell.border = THIN_BORDER
            cell.alignment = Alignment(vertical="center", wrap_text=True)

    # Итоговая строка внизу Листа 1
    ws_buy.append([
        "", "", "ИТОГО ПО ВЕДОМОСТИ:", f"Всего чистых позиций: {len(buy_rows)}",
        "—", float(total_req), 0.0, float(total_def), "", "", "", ""
    ])
    tot_row = ws_buy.max_row
    for c in range(1, 13):
        c_obj = ws_buy.cell(row=tot_row, column=c)
        c_obj.fill = TOTAL_FILL
        c_obj.font = TOTAL_FONT
        c_obj.border = THIN_BORDER

    # --- ЛИСТ 2: ПТО, BIM-КОЛЛИЗИИ И ДОПУСКИ ---
    ws_pto = wb.create_sheet(title="2. ПТО и BIM-сверка")
    pto_headers = (
        "№", "Сквозной BIM-тег / Узел", "Разделы РД", "Оси и отметка",
        "Статус сверки", "Инженерный вывод и рекомендации ПТО", "Ответственный"
    )
    pto_widths = (5, 32, 16, 24, 24, 48, 20)
    _style_header(ws_pto, pto_headers, pto_widths)

    bim_links = list(BimCrossLink.objects.all())
    for idx, bl in enumerate(bim_links, start=1):
        ws_pto.append([
            idx,
            bl.bim_tag,
            f"{bl.source_discipline} ↔ {bl.target_discipline}",
            bl.axes_and_elevation or "По плану",
            bl.get_link_status_display(),
            bl.engineering_note,
            bl.assigned_to,
        ])
        r_num = ws_pto.max_row
        for c in range(1, 8):
            ws_pto.cell(row=r_num, column=c).border = THIN_BORDER
            ws_pto.cell(row=r_num, column=c).alignment = Alignment(vertical="center", wrap_text=True)

    # --- ЛИСТ 3: ЛОГИСТИКА И ОБЪЁМЫ ГПР ---
    ws_log = wb.create_sheet(title="3. Логистика и ГПР")
    log_headers = (
        "№", "Наименование позиции", "Объём", "Ед. изм.",
        "Расчёт логистики и транспорта", "График производства работ (ГПР)"
    )
    log_widths = (5, 38, 14, 10, 42, 38)
    _style_header(ws_log, log_headers, log_widths)

    for idx, r in enumerate(buy_rows, start=1):
        low = r["material_name"].lower()
        if any(w in low for w in ("труб", "пнд", "пэ ", "уголок", "полоса")):
            tr_hint = "Длинномер / бортовой а/м 6 м (погрузка краном/манипулятором)"
        elif "бордюр" in low or "блок" in low or "пазогребнев" in low:
            tr_hint = "Манипулятор / шаланда на поддонах (пакетирование стяжной лентой)"
        elif "кабел" in low:
            tr_hint = "Барабаны на кран-борте с фиксацией клиньями (запрет сбрасывания)"
        else:
            tr_hint = "Сборный груз / малотоннажный фургон (ТК Деловые Линии / ПЭК)"

        ws_log.append([
            idx,
            r["material_name"],
            float(r["required_qty"]),
            r["unit"],
            tr_hint,
            r["schedule_hint"],
        ])
        r_num = ws_log.max_row
        for c in range(1, 7):
            ws_log.cell(row=r_num, column=c).border = THIN_BORDER
            ws_log.cell(row=r_num, column=c).alignment = Alignment(vertical="center", wrap_text=True)

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()
