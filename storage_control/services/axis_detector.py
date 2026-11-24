# -*- coding: utf-8 -*-
import re

# Ось: короткий индекс (А, Б/1, 1-12) на той же строке (без перепрыгивания через \n)
EXPLICIT_AXES_RE = re.compile(
    r'(?:в\s+осях|по\s+осям|оси|ось)[ \t]*[:\-]?[ \t]*([А-ЯA-Z0-9/\.\']{1,5}(?:[ \t]*[-–—][ \t]*[А-ЯA-Z0-9/\.\']{1,5})?)(?=\s|,|\.|;|\)|$)',
    re.IGNORECASE
)

# Настоящая строительная отметка: строго со знаком (+, -, ±) и 3 знаками после точки (напр. -3.450, ±0.000, +4.200)
ELEVATION_RE = re.compile(
    r'(?:отм\.?[ \t]*)?([+-±][ \t]*\d{1,2}[\.,]\d{3})\b',
    re.IGNORECASE
)

MSK_XY_PAIR_RE = re.compile(
    r'(\d{6}[\.,]\d{2})\s+(\d{6}[\.,]\d{2})'
)

GOST_AXIS_LETTERS = set("АБВГДЕЖЗИКЛМНПРСТУФШЩЭЮЯABCDEFGHKLMNPRSTUVXYZ")


def detect_axes_and_elevation(text: str, doc_title: str = "") -> dict:
    """Точно извлекает строительные оси, координаты МСК-71.1 и настоящие отметки высот."""
    if not text:
        return {"axes": "", "geo_coords": "", "elevation": "", "suggested_hazard": "NONE"}

    found_explicit = []
    for m in EXPLICIT_AXES_RE.finditer(text):
        val = re.sub(r'\s+', '', m.group(1)).upper()
        if 1 <= len(val) <= 10 and val not in found_explicit:
            found_explicit.append(val)

    grid_letters = []
    grid_numbers = []
    for raw_line in text.split('\n'):
        token = raw_line.strip().upper()
        if len(token) == 1 and token in GOST_AXIS_LETTERS and token not in grid_letters:
            grid_letters.append(token)
        elif token.isdigit() and 1 <= int(token) <= 60:
            num_val = int(token)
            if num_val not in grid_numbers:
                grid_numbers.append(num_val)

    axes_parts = []
    if found_explicit:
        axes_parts.append("Оси " + ", ".join(found_explicit[:6]))
    if len(grid_letters) >= 2:
        grid_letters.sort()
        axes_parts.append(f"Сетка {grid_letters}–{grid_letters[-1]}")
    if len(grid_numbers) >= 2:
        grid_numbers.sort()
        axes_parts.append(f"Сетка {grid_numbers}–{grid_numbers[-1]}")

    xy_points = []
    for idx, m_xy in enumerate(MSK_XY_PAIR_RE.finditer(text), start=1):
        x_val = m_xy.group(1).replace(',', '.')
        y_val = m_xy.group(2).replace(',', '.')
        entry = (str(idx), x_val, y_val)
        if entry not in xy_points:
            xy_points.append(entry)

    geo_str = ""
    if xy_points:
        formatted_pts = [f"Т.{p} (X={p}, Y={p})" for p in xy_points[:8]]
        geo_str = f"Каталог координат МСК ({len(xy_points)} т.): " + " | ".join(formatted_pts)

    axes_str = " / ".join(axes_parts[:2])
    if geo_str and not axes_str:
        axes_str = geo_str

    elevations = []
    suggested_hazard = "NONE"
    title_low = (doc_title or "").lower()
    if "подзем" in title_low or "котлован" in title_low or "фундамент" in title_low:
        suggested_hazard = "EXCAVATION"

    for m_el in ELEVATION_RE.finditer(text):
        raw_el = m_el.group(1).replace(" ", "").replace(",", ".")
        if raw_el not in elevations:
            elevations.append(raw_el)
        try:
            num_el = float(raw_el.replace("±", ""))
            if num_el <= -1.5:
                suggested_hazard = "EXCAVATION"
            elif num_el >= 1.8 and suggested_hazard == "NONE":
                suggested_hazard = "HEIGHT"
        except ValueError:
            pass

    elev_str = f"Отм. {', '.join(elevations[:4])}" if elevations else ""

    return {
        "axes": axes_str,
        "geo_coords": geo_str,
        "elevation": elev_str,
        "suggested_hazard": suggested_hazard,
    }
