# -*- coding: utf-8 -*-
import io
import re
from datetime import date
import docx
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from storage_control.models import PurchaseRequest
from storage_control.services.section_decoder import resolve_section_and_brigade
from storage_control.services.route_tracer import build_engineering_procurement_rows


def _clean_name(material_text: str) -> str:
    """Убирает служебные квадратные скобки групп ТМЦ и лишние пробелы."""
    if not material_text:
        return ""
    cleaned = re.sub(r'^\[[^\]]+\]\s*', '', str(material_text).strip())
    return cleaned or str(material_text).strip()


HANDOVER_MODES = {
    "GEN_TO_CUSTOMER": (
        "Генподрядчик → Технадзор Заказчика",
        "Представитель лица, осуществляющего строительство (Генподрядчик)",
        "Представитель застройщика / технического заказчика (Стройконтроль)",
    ),
    "SUB_TO_GEN": (
        "Субподрядчик → Генподрядчик (ПТО)",
        "Представитель субподрядной организации (Производитель работ)",
        "Представитель генподрядчика (Инженер ПТО / Начальник участка)",
    ),
    "STAGE_TO_NEXT": (
        "Передача фронта работ смежному участку",
        "Сдающая сторона (Ответственный производитель работ)",
        "Принимающая сторона (Руководитель смежного участка / ПТО)",
    ),
}


def build_aosr_docx_bytes(
    doc,
    handover_mode: str = "GEN_TO_CUSTOMER",
    date_start: str = "",
    date_end: str = "",
    executor_name: str = "Косарев М.В. (Главный Архитектор / ПТО)",
    inspector_name: str = "Представитель строительного контроля Заказчика",
    next_work_allowed: str = "производство последующих строительно-монтажных работ согласно графику ГПР",
    object_title: str = 'ЦОД НПО "СПЛАВ"',
) -> bytes:
    """Генерирует готовый к печати Акт освидетельствования скрытых работ (АОСР .docx) по РД-11-02-2006."""
    document = docx.Document()

    for section in document.sections:
        section.top_margin = Cm(1.5)
        section.bottom_margin = Cm(1.5)
        section.left_margin = Cm(2.0)
        section.right_margin = Cm(1.5)

    style = document.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(11)

    mode_label, sender_role, receiver_role = HANDOVER_MODES.get(
        handover_mode, HANDOVER_MODES["GEN_TO_CUSTOMER"]
    )
    today_str = date.today().strftime("%d.%m.%Y")
    d_start = date_start or today_str
    d_end = date_end or today_str
    obj_name = (object_title or "").strip() or 'ЦОД НПО "СПЛАВ"'

    decoded = resolve_section_and_brigade(doc.title)
    snip_ref = decoded.get("snip_ref") or "СП 48.13330.2019 (Организация строительства)"

    # Шапка объекта
    p_obj = document.add_paragraph()
    p_obj.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r_obj = p_obj.add_run(f"Объект капитального строительства: {obj_name}\n")
    r_obj.bold = True
    p_obj.add_run(f"Контур передачи: {mode_label}")

    # Заголовок акта
    p_title = document.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run(f"\nАКТ № {doc.id}-АОСР\nосвидетельствования скрытых работ\n")
    r_title.bold = True
    r_title.font.size = Pt(13)
    p_title.add_run(f"от «{d_end}» г.  |  Основание: комплект РД {doc.title} (Рев. {doc.revision_num})")

    # Очищенная сводка работ/материалов строго по выбранному тому
    raw_reqs = list(PurchaseRequest.objects.filter(document=doc).order_by("id"))
    clean_rows = [r for r in build_engineering_procurement_rows(raw_reqs) if r["record_type"] == "BUY"]

    p_sec1 = document.add_paragraph()
    p_sec1.add_run("\n1. К освидетельствованию предъявлены следующие работы и конструкции:").bold = True

    table = document.add_table(rows=1, cols=5)
    table.style = "Table Grid"

    hdr_cells = table.rows[0].cells
    headers = ("№", "Помещение / Отметка / Группа", "Наименование выполненных работ и конструкций", "Объём", "Ед. изм.")
    for i, text in enumerate(headers):
        cell = hdr_cells[i]
        cell.text = text
        if cell.paragraphs[0].runs:
            cell.paragraphs[0].runs[0].bold = True

    if clean_rows:
        for idx, item in enumerate(clean_rows, start=1):
            row_cells = table.add_row().cells
            grp_clean = _clean_name(item["node_cabinet"])
            loc = " / ".join(filter(None, [item["location"], grp_clean])) or "По проекту"
            row_cells[0].text = str(idx)
            row_cells[1].text = loc
            row_cells[2].text = item["material_name"]
            row_cells[3].text = f"{float(item['required_qty']):.2f}"
            row_cells[4].text = item["unit"]
    else:
        row_cells = table.add_row().cells
        row_cells[0].text = "1"
        row_cells[1].text = "Согласно листам тома"
        row_cells[2].text = f"Комплекс скрытых работ по тому {doc.title}"
        row_cells[3].text = "1.00"
        row_cells[4].text = "компл."

    # Раздел 2: Применённые материалы и сертификаты
    p_sec2 = document.add_paragraph()
    p_sec2.add_run("\n2. При выполнении работ применены материалы и изделия:\n").bold = True
    if clean_rows:
        mat_names = "; ".join(f"{r['material_name']} ({r['required_qty']} {r['unit']})" for r in clean_rows[:12])
        p_sec2.add_run(f"   {mat_names}.\n   Паспорта качества и сертификаты соответствия приложены к настоящему Акту.")
    else:
        p_sec2.add_run("   Материалы согласно спецификации проекта (сертификаты и паспорта качества приложены).")

    # Раздел 3: Даты и решение комиссии
    p_terms = document.add_paragraph()
    p_terms.add_run("\n3. Даты выполнения скрытых работ:\n").bold = True
    p_terms.add_run(f"   Начало работ: «{d_start}» г.    Окончание работ: «{d_end}» г.\n")

    p_terms.add_run("\n4. Решение комиссии:\n").bold = True
    p_terms.add_run(
        f"   Работы выполнены в соответствии с проектной документацией ({doc.title}) "
        f"и требованиями {snip_ref}.\n"
        f"   На основании изложенного разрешается: {next_work_allowed}."
    )

    # Блок подписей
    p_signs = document.add_paragraph()
    p_signs.add_run("\nПОДПИСИ ОТВЕТСТВЕННЫХ ЛИЦ:\n").bold = True
    p_signs.add_run(
        f"\nСдал ({sender_role}):\n"
        f"_______________________ / {executor_name} /\n"
        f"\nПринял ({receiver_role}):\n"
        f"_______________________ / {inspector_name} /\n"
    )

    buf = io.BytesIO()
    document.save(buf)
    return buf.getvalue()
