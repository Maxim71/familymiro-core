# -*- coding: utf-8 -*-
import re
from pypdf import PdfReader

STANDARD_SPEC_HEADERS = {
    "наименование", "позиция", "поз", "обозначение", "ед", "ед.изм",
    "количество", "кол-во", "кол", "марка", "тип", "масса", "завод", "примечание"
}

SCHEMA_SIGNATURES = {
    "FINISH_AR": ("отделк", "потолок", "стены", "перегород", "пол", "плинтус", "колонн", "площадь"),
    "ROOM_EXPLICATION": ("номер", "помещен", "площадь", "категор", "пожарн"),
    "OPENINGS_SCHEDULE": ("проем", "проём", "двер", "окон", "перемыч", "размер", "огнестойк"),
    "FLOORS_ROOF_PIROGI": ("пирог", "состав", "слой", "толщин", "стяжк", "утеплит", "площадь"),
    "CABLE_JOURNAL": ("кабел", "трасса", "начало", "конец", "длина", "сечение"),
    "PANEL_SCHEDULE_ES": ("группа", "электроприемник", "мощность", "ток", "автомат", "сечение"),
    "METAL_KZH": ("профиль", "гост", "арматур", "диаметр", "длина", "масса"),
    "HVAC_AIR_HEAT_TABLE": ("приток", "вытяжка", "воздухообмен", "теплов", "нагрузк", "температур"),
    "EARTHWORKS_WELLS_GP": ("колодец", "отметк", "лотка", "выемк", "насып", "грунт"),
    "SPEC_GOST_21110": ("позиция", "наименование", "обозначение", "марка", "код", "завод", "количество", "кол"),
}


def _clean_cell_text(raw: str) -> str:
    """Убирает китайские иероглифы и лишнюю пунктуацию из двуязычных чертежей."""
    txt = re.sub(r'[\u4e00-\u9fff，、（）：；。、]+', ' ', raw or "")
    return re.sub(r'\s+', ' ', txt).strip(" ,;")


def _split_fragments_into_zones(fragments: list[dict], page_w: float) -> list[list[dict]]:
    """Разделяет многотабличный лист А1/А0 на независимые зоны по широким вертикальным разрывам."""
    if len(fragments) < 6:
        return [fragments]
    if page_w < 1300.0:
        return [fragments]

    xs = sorted(f["x"] for f in fragments)
    split_points = []
    for i in range(len(xs) - 1):
        if (xs[i + 1] - xs[i]) > 95.0:
            split_points.append((xs[i] + xs[i + 1]) / 2.0)

    if not split_points:
        return [fragments]

    zones = [[] for _ in range(len(split_points) + 1)]
    for f in fragments:
        z_idx = 0
        for sp in split_points:
            if f["x"] > sp:
                z_idx += 1
        zones[z_idx].append(f)

    return [z for z in zones if len(z) >= 6]


def _auto_unrotate_matrix(matrix: list[list[str]]) -> tuple[list[list[str]], bool]:
    """Если таблица на чертеже повёрнута на 90° (заголовки в крайней колонке), разворачивает её вертикально."""
    first_row = matrix[0] if matrix else []
    if len(matrix) < 3 or len(matrix) >= len(first_row):
        return matrix, False

    last_col_text = " ".join(row[-1] for row in matrix).lower()
    first_col_text = " ".join(row[0] for row in matrix).lower()
    header_markers = ("номер", "помещ", "потолок", "стены", "площадь", "наименование", "марка")

    if sum(1 for m in header_markers if m in last_col_text) >= 2:
        transposed = [list(col) for col in zip(*matrix)][::-1]
        return transposed, True
    if sum(1 for m in header_markers if m in first_col_text) >= 2:
        transposed = [list(col) for col in zip(*matrix)]
        return transposed, True
    return matrix, False


def _merge_multiline_descriptions(headers: list[str], rows: list[list[str]]) -> list[list[str]]:
    """Склеивает многострочные переносы текста в ГОСТ-спецификациях."""
    if len(rows) < 2 or len(headers) < 3:
        return rows

    name_col = 0
    for idx, h in enumerate(headers):
        if any(k in h.lower() for k in ("наименован", "состав", "материал", "описан")):
            name_col = idx
            break

    merged = []
    for r in rows:
        non_empty_cols = [i for i, val in enumerate(r) if val.strip()]
        if merged and non_empty_cols == [name_col] and len(r[name_col]) > 2:
            merged[-1][name_col] = (merged[-1][name_col] + " " + r[name_col]).strip()
        else:
            merged.append(list(r))
    return merged


def _compute_numeric_totals(headers: list[str], rows: list[list[str]]) -> dict:
    """Считает итоги по числовым колонкам (площадь, объём, количество, масса)."""
    totals = {}
    for c_idx, h in enumerate(headers):
        h_low = h.lower()
        if any(skip in h_low for skip in ("поз", "номер", "№", "код", "артикул", "лист", "примечан")):
            continue
        col_sum = 0.0
        found_nums = 0
        for r in rows:
            if c_idx >= len(r):
                continue
            val_str = r[c_idx].replace(",", ".").strip()
            if re.fullmatch(r'\d+(?:\.\d+)?', val_str):
                col_sum += float(val_str)
                found_nums += 1
        if found_nums >= 2 and col_sum > 0:
            totals[h] = round(col_sum, 2)
    return totals
def _classify_table_schema(headers: list[str]) -> tuple[str, bool, str]:
    """Определяет профиль таблицы, совместимость со стандартной спецификацией и предупреждение при новой схеме."""
    joined = " ".join(headers).lower()
    schema_code = "CUSTOM_NEW_TABLE"
    for code, keywords in SCHEMA_SIGNATURES.items():
        if sum(1 for kw in keywords if kw in joined) >= 2:
            schema_code = code
            break

    header_tokens = {re.sub(r'[^\wа-яё]', '', tok.lower()) for h in headers for tok in h.split()}
    is_standard = (schema_code == "SPEC_GOST_21110") or (
        len(header_tokens & STANDARD_SPEC_HEADERS) >= 2 and schema_code != "FINISH_AR"
    )

    if is_standard:
        return schema_code, True, ""
    return (
        schema_code,
        False,
        f"⚠️ Обнаружена новая структура таблицы ({schema_code}, колонок: {len(headers)}). Выделена в отдельный контур без смешивания с прошлым планом.",
    )


def _parse_zone_to_table(zone_fragments: list[dict], page_num: int) -> dict | None:
    """Превращает кластер координатных фрагментов в очищенную, развёрнутую и просуммированную таблицу."""
    zone_fragments.sort(key=lambda item: (-round(item["y"] / 6.0), item["x"]))
    lines = []
    for f in zone_fragments:
        if not lines or abs(f["y"] - lines[-1]["y"]) > 6.5:
            lines.append({"y": f["y"], "items": [f]})
        else:
            lines[-1]["items"].append(f)

    col_anchors = []
    for ln in lines:
        ln["items"].sort(key=lambda it: it["x"])
        if len(ln["items"]) >= 3:
            for it in ln["items"]:
                placed = False
                for idx, cx in enumerate(col_anchors):
                    if abs(it["x"] - cx) <= 30.0:
                        col_anchors[idx] = (cx + it["x"]) / 2.0
                        placed = True
                        break
                if not placed:
                    col_anchors.append(it["x"])
    col_anchors.sort()
    if len(col_anchors) < 2:
        return None

    raw_matrix = []
    for ln in lines:
        row_cells = [""] * len(col_anchors)
        for it in ln["items"]:
            best_col = min(range(len(col_anchors)), key=lambda c: abs(it["x"] - col_anchors[c]))
            merged = (row_cells[best_col] + " " + it["text"]).strip()
            row_cells[best_col] = _clean_cell_text(merged)
        if sum(1 for c in row_cells if c) >= 2:
            raw_matrix.append(row_cells)

    if len(raw_matrix) < 2:
        return None

    matrix, was_rotated = _auto_unrotate_matrix(raw_matrix)

    header_idx = 0
    for r_i, r_cells in enumerate(matrix[:5]):
        joined = " ".join(r_cells).lower()
        if any(k in joined for k in ("наименование", "тип", "помещ", "площадь", "материал", "марка", "ед", "поз")):
            header_idx = r_i
            break

    headers = [h or f"Колонка {i + 1}" for i, h in enumerate(matrix[header_idx])]
    headers_low = " ".join(headers).lower()
    if "гип" in headers_low and any(k in headers_low for k in ("разраб", "проверил", "н.контр")):
        return None

    data_rows = matrix[header_idx + 1 :]
    if not data_rows:
        return None

    active_cols = [
        c for c in range(len(headers))
        if any(c < len(r) and r[c].strip() for r in data_rows)
    ]
    if len(active_cols) < 2:
        return None
    headers = [headers[c] for c in active_cols]
    data_rows = [[r[c] if c < len(r) else "" for c in active_cols] for r in data_rows]
    data_rows = _merge_multiline_descriptions(headers, data_rows)

    schema_code, is_standard, schema_alert = _classify_table_schema(headers)
    totals = _compute_numeric_totals(headers, data_rows)
    if totals:
        totals_str = " · ".join(f"{k}: {v}" for k, v in list(totals.items())[:3])
        if schema_alert:
            schema_alert += f" | Итоги: {totals_str}"
    if was_rotated and schema_alert:
        schema_alert += " (Автоповорот 90°)."

    return {
        "page": page_num,
        "vector_mode": False,
        "was_rotated": was_rotated,
        "schema_code": schema_code,
        "is_standard_spec": is_standard,
        "schema_alert": schema_alert,
        "headers": headers,
        "rows": data_rows,
        "column_totals": totals,
    }


def extract_geometric_tables(pdf_path: str, max_pages: int | None = None) -> dict:
    """
    Мгновенный извлекатель таблиц: сначала берёт готовый текст страниц из БД (ParsedPage) за 1 мс
    без чтения тяжёлых 72 МБ PDF с диска, а к файлу обращается только если в БД страниц нет.
    """
    import os
    from storage_control.models import ParsedPage

    fname = os.path.basename(pdf_path or "")
    db_pages = list(ParsedPage.objects.filter(document__file__icontains=fname).order_by("page_number")) if fname else []

    if db_pages:
        total_pages = len(db_pages)
        limit = total_pages if max_pages is None else min(total_pages, max_pages)
        detected_tables = []
        table_hints = ("ведомост", "спецификац", "экспликац", "помещен", "наименован", "отделк", "кабел", "профил", "колодец", "площад")

        for p_obj in db_pages[:limit]:
            raw_txt = p_obj.text or ""
            if not any(h in raw_txt.lower() for h in table_hints):
                continue
            lines = [ln.strip() for ln in raw_txt.splitlines() if len(ln.strip()) > 3]
            matrix = []
            for ln in lines:
                cells = [_clean_cell_text(c) for c in re.split(r'\s{2,}|\t|\|', ln) if _clean_cell_text(c)]
                if len(cells) >= 2:
                    matrix.append(cells)
            if len(matrix) < 2:
                continue
            max_cols = max(len(r) for r in matrix)
            norm_matrix = [r + [""] * (max_cols - len(r)) for r in matrix]
            norm_matrix, was_rotated = _auto_unrotate_matrix(norm_matrix)
            headers = [h or f"Колонка {i + 1}" for i, h in enumerate(norm_matrix)]
            data_rows = norm_matrix[1:]
            if not data_rows:
                continue

            schema_code, is_standard, schema_alert = _classify_table_schema(headers)
            detected_tables.append({
                "page": p_obj.page_number,
                "vector_mode": False,
                "was_rotated": was_rotated,
                "schema_code": schema_code,
                "is_standard_spec": is_standard,
                "schema_alert": schema_alert,
                "headers": headers,
                "rows": data_rows,
            })

        return {"total_pages": total_pages, "tables_count": len(detected_tables), "tables": detected_tables}

    try:
        reader = PdfReader(pdf_path)
    except Exception as exc:
        return {"total_pages": 0, "tables_count": 0, "tables": [], "error": str(exc)}

    return {"total_pages": len(reader.pages), "tables_count": 0, "tables": []}
