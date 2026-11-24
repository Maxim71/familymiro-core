# -*- coding: utf-8 -*-
import io
import re
from datetime import date, timedelta
from decimal import Decimal
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from storage_control.models import Document, PurchaseRequest
from storage_control.services.smart_router import is_noise_for_document

HEADER_FILL = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
HEADER_FONT = Font(name="Calibri", size=11, bold=True, color="38BDF8")
MILESTONE_FILL = PatternFill(start_color="E0F2FE", end_color="E0F2FE", fill_type="solid")
THIN_BORDER = Border(
    left=Side(style="thin", color="CBD5E1"),
    right=Side(style="thin", color="CBD5E1"),
    top=Side(style="thin", color="CBD5E1"),
    bottom=Side(style="thin", color="CBD5E1"),
)

DISCIPLINE_RULES = {
    "ГП":   (10, "Подготовка территории, геодезия и вертикальная планировка", Decimal("500"), "Старт работ на площадке"),
    "КЖ":   (20, "Земляные работы и монолитный железобетон", Decimal("350"), "После разбивки осей и шурфления"),
    "КМ":   (30, "Монтаж несущих металлоконструкций", Decimal("15"), "После набора прочности фундаментов"),
    "ННС":  (35, "Наружные инженерные сети и колодцы", Decimal("120"), "До обратной засыпки и благоустройства"),
    "ЗКВС": (36, "Наружные сети водоснабжения и канализации", Decimal("120"), "До устройства дорожной одежды"),
    "АР":   (40, "Архитектурно-строительные работы, кровля и фасад", Decimal("180"), "После закрытия несущего каркаса"),
    "ОВ":   (50, "Отопление, вентиляция и кондиционирование", Decimal("90"), "После устройства перегородок и проёмов"),
    "ВК":   (52, "Внутренний водопровод и канализация", Decimal("80"), "Параллельно с общестроительными работами"),
    "ЭС":   (55, "Электроснабжение и силовое оборудование", Decimal("150"), "После оштукатуривания и закрытия контура"),
    "СПА":  (58, "Пожарная автоматика, сигнализация и оповещение (СПА/АПС)", Decimal("30"), "После монтажа кабельных трасс"),
    "СКС":  (60, "Структурированные кабельные системы и АСУ ТП", Decimal("25"), "После чистовой отделки серверных и пом."),
    "АИ":   (70, "Архитектурные интерьеры и чистовая отделка", Decimal("120"), "После завершения скрытых инженерных трасс"),
}


def _extract_book_sort_key(doc_title: str) -> tuple:
    upper = (doc_title or "").upper()
    disc_order = 90
    for code, rule in DISCIPLINE_RULES.items():
        if code in upper:
            disc_order = rule[0]
            break

    m_num = re.search(r'(?:КЖ|АР|АСКС|СПА|ОВ|ВК|ЭС|ГП|ННС|КМ)\s*0*(\d+(?:[\.,]\d+)?)', upper)
    book_num = float(m_num.group(1).replace(',', '.')) if m_num else 999.0
    return (disc_order, book_num, doc_title)


def _add_work_days(start_dt: date, days: int) -> date:
    cur = start_dt
    added = 0
    while added < max(1, days):
        cur += timedelta(days=1)
        if cur.weekday() < 5:
            added += 1
    return cur


def _is_valid_gpr_item(doc_title: str, item: PurchaseRequest) -> bool:
    raw = (item.material_name or "").strip()
    low = raw.lower()
    if len(raw) < 6 or re.search(r'[\u4e00-\u9fff]', raw):
        return False
    if is_noise_for_document(doc_title, raw):
        return False
    if re.match(r'^(?:наименование|площадь|итого|всего|типотделки|объем|объём)\b', low):
        return False
    return True


def _clean_gpr_qty(item: PurchaseRequest) -> Decimal:
    qty = item.required_qty or Decimal("1")
    u = (item.unit or "").strip().lower()
    # Отсекаем 5-9 значные заводские артикулы (9368002, 425533, 250003) в штучных позициях
    if u in ("шт", "шт.", "компл", "компл.") and qty >= Decimal("2500"):
        return Decimal("1")
    return qty


def build_customer_gpr_excel(doc_id=None, start_date: date = None) -> bytes:
    """
    Контур №2: Генерирует чистый Календарный график производства работ (ГПР) для Заказчика (.xlsx)
    без дублей томов, без мусорных шапок и без искажения сроков из-за заводских артикулов.
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Календарный график (ГПР)"

    headers = (
        "№ п/п", "Раздел РД", "Том-основание", "Наименование этапа / комплекса работ",
        "Физический объём", "Ед. изм.", "Расчётная длительность (смен)",
        "Плановый старт", "Плановый финиш", "Технологическая связь и аргументация"
    )
    widths = (7, 12, 24, 38, 16, 10, 16, 14, 14, 42)

    ws.append(list(headers))
    for idx, w in enumerate(widths, start=1):
        c = ws.cell(row=1, column=idx)
        c.fill = HEADER_FILL
        c.font = HEADER_FONT
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = THIN_BORDER
        ws.column_dimensions[openpyxl.utils.get_column_letter(idx)].width = w
    ws.row_dimensions.height = 30
    ws.freeze_panes = "A2"

    docs_qs = Document.objects.exclude(work_status="ARCHIVED").order_by("-revision_num", "-id")
    if doc_id:
        docs_qs = docs_qs.filter(id=doc_id)

    # Оставляем по одному актуальному экземпляру каждого тома (убираем дубли повторных загрузок)
    unique_docs = {}
    for d in docs_qs:
        if d.title not in unique_docs:
            unique_docs[d.title] = d

    sorted_docs = sorted(unique_docs.values(), key=lambda d: _extract_book_sort_key(d.title))
    cursor_date = start_date or date.today()
    step_num = 0

    for doc in sorted_docs:
        raw_reqs = list(PurchaseRequest.objects.filter(document=doc))
        reqs = [r for r in raw_reqs if _is_valid_gpr_item(doc.title, r)]
        if not reqs:
            continue

        disc = reqs[0].discipline or "РД"
        if "СПА" in doc.title.upper():
            disc = "СПА"
        _, default_stage_name, norm_per_shift, tech_link = DISCIPLINE_RULES.get(
            disc, (90, f"Комплекс работ по разделу {disc}", Decimal("50"), "Согласно проекту РД")
        )

        tep_list = [r for r in reqs if r.record_type == "TEP"]
        buy_list = [r for r in reqs if r.record_type == "BUY"]

        if tep_list:
            for item in tep_list:
                step_num += 1
                qty = _clean_gpr_qty(item)
                if "ручн" in item.material_name.lower() or "добор" in item.material_name.lower():
                    rate = Decimal("35")
                elif "выемк" in item.material_name.lower() or "котлован" in item.material_name.lower():
                    rate = Decimal("450")
                else:
                    rate = norm_per_shift

                shifts = max(1, min(90, int((qty / rate).to_integral_value())))
                end_dt = _add_work_days(cursor_date, shifts)
                pred_txt = f"После этапа №{step_num - 1}; {tech_link}" if step_num > 1 else tech_link

                ws.append([
                    step_num, disc, doc.title, item.material_name,
                    float(qty), item.unit, shifts,
                    cursor_date.strftime("%d.%m.%Y"), end_dt.strftime("%d.%m.%Y"),
                    pred_txt
                ])
                r_num = ws.max_row
                for col in range(1, 11):
                    ws.cell(row=r_num, column=col).border = THIN_BORDER
                    ws.cell(row=r_num, column=col).alignment = Alignment(vertical="center", wrap_text=True)
                cursor_date = end_dt

        if buy_list:
            step_num += 1
            total_qty = sum((_clean_gpr_qty(b) for b in buy_list), Decimal("0"))
            main_unit = buy_list[0].unit
            shifts = max(2, min(60, int((total_qty / norm_per_shift).to_integral_value())))
            end_dt = _add_work_days(cursor_date, shifts)
            pred_txt = f"После этапа №{step_num - 1}; {tech_link}" if step_num > 1 else tech_link
            stage_label = f"{default_stage_name} ({len(buy_list)} поз. по спецификации)"

            ws.append([
                step_num, disc, doc.title, stage_label,
                float(total_qty), main_unit, shifts,
                cursor_date.strftime("%d.%m.%Y"), end_dt.strftime("%d.%m.%Y"),
                pred_txt
            ])
            r_num = ws.max_row
            for col in range(1, 11):
                ws.cell(row=r_num, column=col).border = THIN_BORDER
                ws.cell(row=r_num, column=col).alignment = Alignment(vertical="center", wrap_text=True)
            cursor_date = end_dt

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()
