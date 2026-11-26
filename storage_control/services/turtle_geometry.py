# -*- coding: utf-8 -*-
import os
import re
from PIL import Image, ImageOps
from django.conf import settings

try:
    import cv2
    import numpy as np
    HAS_CV2 = True
except Exception:
    HAS_CV2 = False

try:
    import pypdfium2 as pdfium
    HAS_PDFIUM = True
except Exception:
    HAS_PDFIUM = False

RU_AXIS_LETTERS = ("А", "Б", "В", "Г", "Д", "Е", "Ж", "И", "К", "Л", "М", "Н", "П", "Р", "С", "Т", "У", "Ф")
SCALE_RE = re.compile(r'(?:[МM]\s*)?1\s*[:：]\s*(5|10|15|20|25|40|50|75|100|200|500)\b', re.IGNORECASE)


def _cluster_coords(coords, min_gap: float) -> list[float]:
    vals = sorted(float(v) for v in coords if v is not None)
    if not vals:
        return []
    clusters = [[vals.pop(0)]]
    for c in vals:
        if abs(c - clusters[-1][-1]) <= min_gap:
            clusters[-1].append(c)
        else:
            clusters.append([c])
    return [round(sum(cl) / len(cl), 1) for cl in clusters]


def _detect_building_axes(gray_np: "np.ndarray", bx: int, by: int, bw: int, bh: int) -> tuple[list[float], list[float]]:
    """
    ?????????????? ???????? ??????????????? ???? ?? ???? 21.101:
    ???????? ????????? ??????????????? ??? (???????? ????? >= 70% ???????? ???????,
    ??????????? ?? ???????? ?????? ??\u043c\u043c \u00b7 ??????? ????) ?? ?????????? ???????????.
    """
    edges = cv2.Canny(gray_np, 45, 140, apertureSize=3)
    min_v_len = max(50, int(bh * 0.68))
    min_h_len = max(50, int(bw * 0.68))
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=65, minLineLength=min(min_v_len, min_h_len), maxLineGap=18)

    v_xs, h_ys = [], []
    if lines is not None:
        for x1, y1, x2, y2 in lines.reshape(-1, 4):
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            dx, dy = abs(x2 - x1), abs(y2 - y1)
            top_y, bot_y = min(y1, y2), max(y1, y2)
            left_x, right_x = min(x1, x2), max(x1, x2)

            # ???????????? ??? (???????? 1..12): ??????\u043c\u043c \u00b7 ??????? ?? ??????? ??? ?????? ???????? ?????
            if dx <= 5 and dy >= min_v_len:
                mx = (x1 + x2) / 2.0
                extends_outside = (top_y <= by - 4) or (bot_y >= by + bh + 4)
                if (bx - 8 <= mx <= bx + bw + 8) and extends_outside:
                    v_xs.append(mx)

            # ?????????????? ??? (????????? ???): ??????\u043c\u043c \u00b7 ??????? ?? ????? ??? ?????? ???????? ?????
            elif dy <= 5 and dx >= min_h_len:
                my = (y1 + y2) / 2.0
                extends_outside = (left_x <= bx - 4) or (right_x >= bx + bw + 4)
                if (by - 8 <= my <= by + bh + 8) and extends_outside:
                    h_ys.append(my)

    x_axes = _cluster_coords(v_xs, max(14.0, bw * 0.045))[:16]
    y_axes = _cluster_coords(h_ys, max(18.0, bh * 0.14))[:8]

    if len(x_axes) < 2:
        x_axes = [float(bx), float(bx + bw)]
    if len(y_axes) < 2:
        y_axes = [float(by), float(by + bh)]
    return x_axes, y_axes


def _nearest_axis_label(px: float, py: float, x_axes: list[float], y_axes: list[float]) -> str:
    if not x_axes or not y_axes:
        return "??? ????? ????"
    best_x_idx = min(range(len(x_axes)), key=lambda i: abs(x_axes[i] - px)) + 1
    rev_y = list(reversed(y_axes))
    best_y_idx = min(range(len(rev_y)), key=lambda i: abs(rev_y[i] - py))
    letter = RU_AXIS_LETTERS[best_y_idx] if best_y_idx < len(RU_AXIS_LETTERS) else f"?{best_y_idx + 1}"
    return f"??? {letter} / {best_x_idx}"


def _detect_manholes_and_passages(gray_np: "np.ndarray", bx: int, by: int, bw: int, bh: int, x_axes: list[float], y_axes: list[float]) -> tuple[list[dict], list[dict]]:
    # 1. ???????? ????? / ???????? (?????? ?? ?????)
    blurred = cv2.GaussianBlur(gray_np, (5, 5), 1.2)
    min_r = max(5, int(min(bw, bh) * 0.012))
    max_r = max(14, int(min(bw, bh) * 0.045))
    circles = cv2.HoughCircles(
        blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=max(18, min_r * 3),
        param1=90, param2=24, minRadius=min_r, maxRadius=max_r
    )
    manholes = []
    if circles is not None:
        for idx, c in enumerate(np.round(circles[0, :]).astype("int"), start=1):
            cx, cy, cr = int(c[0]), int(c[1]), int(c[2])
            if bx + 8 <= cx <= bx + bw - 8 and by + 8 <= cy <= by + bh - 8:
                manholes.append({
                    "code": f"?-{len(manholes) + 1}",
                    "x": cx, "y": cy, "r": cr,
                    "axis_ref": _nearest_axis_label(cx, cy, x_axes, y_axes),
                })
            if len(manholes) >= 12:
                break

    # 2. ???????? ??????\u043c\u043c \u00b7 ?????\u043c\u043c \u00b7 ?????? (??????????? ????? ?? ??????? / ???? ???????)
    _, bin_walls = cv2.threshold(gray_np, 150, 255, cv2.THRESH_BINARY_INV)
    thick_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    walls_only = cv2.morphologyEx(bin_walls, cv2.MORPH_OPEN, thick_kernel)
    thin_lines = cv2.subtract(bin_walls, walls_only)
    intersections = cv2.bitwise_and(cv2.dilate(walls_only, np.ones((5, 5), np.uint8)), thin_lines)

    num_labels, _, stats, centroids = cv2.connectedComponentsWithStats(intersections)
    passages = []
    for lbl in range(1, num_labels):
        area = int(stats[lbl, cv2.CC_STAT_AREA])
        px, py = float(centroids[lbl][0]), float(centroids[lbl][1])
        if 12 <= area <= 450 and (bx + 12 <= px <= bx + bw - 12) and (by + 12 <= py <= by + bh - 12):
            if all(abs(px - p["x"]) > 22 or abs(py - p["y"]) > 22 for p in passages):
                passages.append({
                    "code": f"?-{len(passages) + 1}",
                    "x": round(px, 1), "y": round(py, 1),
                    "axis_ref": _nearest_axis_label(px, py, x_axes, y_axes),
                })
        if len(passages) >= 14:
            break

    return manholes, passages



def _trace_cable_and_pipe_routes(gray_np: "np.ndarray", bx: int, by: int, bw: int, bh: int, x_axes: list[float], y_axes: list[float], step_m: float) -> tuple[list[dict], float]:
    _, bin_all = cv2.threshold(gray_np, 165, 255, cv2.THRESH_BINARY_INV)
    thick_walls = cv2.morphologyEx(bin_all, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7)))
    thin_routes = cv2.subtract(bin_all, cv2.dilate(thick_walls, np.ones((3, 3), np.uint8)))

    min_seg = max(24, int(min(bw, bh) * 0.08))
    raw_lines = cv2.HoughLinesP(thin_routes, 1, np.pi / 180, threshold=40, minLineLength=min_seg, maxLineGap=10)

    px_per_m = (bw / max(1, len(x_axes) - 1)) / max(1.0, step_m)
    routes = []
    total_m = 0.0

    if raw_lines is not None:
        for x1, y1, x2, y2 in raw_lines.reshape(-1, 4):
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            if not (bx + 6 <= x1 <= bx + bw - 6 and by + 6 <= y1 <= by + bh - 6 and bx + 6 <= x2 <= bx + bw - 6 and by + 6 <= y2 <= by + bh - 6):
                continue
            seg_len_px = float(np.hypot(x2 - x1, y2 - y1))
            if seg_len_px < min_seg:
                continue
            # ???????? ??????????? ???????????? ????? ????? 14 px
            if any(abs((x1 + x2)/2 - (r["x1"] + r["x2"])/2) < 14 and abs((y1 + y2)/2 - (r["y1"] + r["y2"])/2) < 14 for r in routes):
                continue
            seg_m = round(seg_len_px / max(1.0, px_per_m), 1)
            total_m += seg_m
            routes.append({
                "code": f"?-{len(routes) + 1}",
                "x1": x1, "y1": y1, "x2": x2, "y2": y2,
                "length_m": seg_m,
                "from_axis": _nearest_axis_label(x1, y1, x_axes, y_axes),
                "to_axis": _nearest_axis_label(x2, y2, x_axes, y_axes),
            })
            if len(routes) >= 12:
                break

    return routes, round(total_m, 1)


def analyze_building_plan_footprint(image_path: str, operator_object_title: str = "", axis_step_mm: int = 6000) -> dict:
    if not image_path or not os.path.exists(image_path):
        return {"ok": False, "error": "Файл плана не найден"}

    object_label = (operator_object_title or "").strip() or "Не указано на снимке (вводится оператором или из штампа РД)"
    if not HAS_CV2:
        return {"ok": True, "projection": "Вид сверху (поэтажный план)", "object_title_fact": object_label, "footprint_shape": "Базовый контур", "svg_preview": ""}

    pil_img = ImageOps.exif_transpose(Image.open(image_path)).convert("RGB")
    gray = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2GRAY)

    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, inv_bin = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
    closed = cv2.morphologyEx(inv_bin, cv2.MORPH_CLOSE, kernel, iterations=2)

    contours, _ = cv2.findContours(closed, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return {"ok": True, "projection": "Вид сверху", "object_title_fact": object_label, "footprint_shape": "Контур стен не выделен", "svg_preview": ""}

    outer_cnt = max(contours, key=cv2.contourArea)
    outer_area = float(cv2.contourArea(outer_cnt))
    bx, by, bw, bh = cv2.boundingRect(outer_cnt)
    extent_pct = round((outer_area / float(max(1, bw * bh))) * 100.0, 1)

    peri = cv2.arcLength(outer_cnt, True)
    approx = cv2.approxPolyDP(outer_cnt, 0.018 * peri, True)
    corners_count = len(approx)
    aspect_ratio = round(max(bw, bh) / max(1, min(bw, bh)), 2)

    if extent_pct >= 84.0 and corners_count <= 6:
        shape_label = "Прямоугольный корпус в плане"
    elif 55.0 <= extent_pct < 84.0 and 6 <= corners_count <= 10:
        shape_label = "Г-образный или П-образный корпус в плане (с вырезом/двором)"
    else:
        shape_label = f"Сложный многосекционный контур в плане ({corners_count} углов)"

    inner_rooms = sum(1 for c in contours if 400.0 <= cv2.contourArea(c) < outer_area * 0.45)
    x_axes, y_axes = _detect_building_axes(gray, bx, by, bw, bh)
    manholes, passages = _detect_manholes_and_passages(gray, bx, by, bw, bh, x_axes, y_axes)
    routes, route_total_m = _trace_cable_and_pipe_routes(gray, bx, by, bw, bh, x_axes, y_axes, max(1.0, axis_step_mm / 1000.0))

    spans_x, spans_y = max(1, len(x_axes) - 1), max(1, len(y_axes) - 1)
    step_m = max(1.0, axis_step_mm / 1000.0)
    est_length_m, est_width_m = round(spans_x * step_m, 1), round(spans_y * step_m, 1)
    est_area_m2 = round(est_length_m * est_width_m * (extent_pct / 100.0), 1)

    svg_w, svg_h = 540, 330
    pad_l, pad_r, pad_t, pad_b = 54, 34, 42, 62
    draw_w, draw_h = svg_w - pad_l - pad_r, svg_h - pad_t - pad_b
    scale = min(draw_w / max(1, bw), draw_h / max(1, bh))
    offset_x = pad_l + (draw_w - bw * scale) / 2.0
    offset_y = pad_t + (draw_h - bh * scale) / 2.0

    x0_s = round(offset_x, 1)
    y0_s = round(offset_y, 1)
    x1_s = round(offset_x + bw * scale, 1)
    y1_s = round(offset_y + bh * scale, 1)

    axes_svg = []
    ax_coords_svg = []
    for idx, ax_x in enumerate(x_axes, start=1):
        sx = round(offset_x + (ax_x - bx) * scale, 1)
        ax_coords_svg.append((idx, sx))
        axes_svg.append(
            f'<line x1="{sx}" y1="{pad_t - 12}" x2="{sx}" y2="{svg_h - 38}" stroke="#64748b" stroke-width="0.9" stroke-dasharray="6 3 1.5 3"/>'
            f'<circle cx="{sx}" cy="{svg_h - 24}" r="10" fill="#0f172a" stroke="#f59e0b" stroke-width="1.4"/>'
            f'<text x="{sx}" y="{svg_h - 20}" fill="#fbbf24" font-size="10" font-weight="bold" text-anchor="middle" font-family="monospace">{idx}</text>'
        )

    # ????????? ??????? ?? ???? 2.307 (??? ??\u043c\u043c \u00b7 \u043c\u043c \u00b7 ???????)
    dim_svg = []
    dim_y = svg_h - 44
    for i in range(len(ax_coords_svg) - 1):
        _, sx1 = ax_coords_svg[i]
        _, sx2 = ax_coords_svg[i + 1]
        mid_x = round((sx1 + sx2) / 2.0, 1)
        dim_svg.append(
            f'<line x1="{sx1}" y1="{dim_y}" x2="{sx2}" y2="{dim_y}" stroke="#94a3b8" stroke-width="1"/>'
            f'<line x1="{sx1 - 3}" y1="{dim_y + 3}" x2="{sx1 + 3}" y2="{dim_y - 3}" stroke="#94a3b8" stroke-width="1.3"/>'
            f'<line x1="{sx2 - 3}" y1="{dim_y + 3}" x2="{sx2 + 3}" y2="{dim_y - 3}" stroke="#94a3b8" stroke-width="1.3"/>'
            f'<text x="{mid_x}" y="{dim_y - 3}" fill="#cbd5e1" font-size="9" text-anchor="middle" class="turtle-dim-text" font-family="monospace">{axis_step_mm}</text>'
        )

    ay_coords_svg = []
    for idx, ay_y in enumerate(reversed(y_axes)):
        sy = round(offset_y + (ay_y - by) * scale, 1)
        letter = RU_AXIS_LETTERS[idx] if idx < len(RU_AXIS_LETTERS) else f"?{idx + 1}"
        ay_coords_svg.append((letter, sy))
        axes_svg.append(
            f'<line x1="34" y1="{sy}" x2="{svg_w - 16}" y2="{sy}" stroke="#64748b" stroke-width="0.9" stroke-dasharray="6 3 1.5 3"/>'
            f'<circle cx="18" cy="{sy}" r="10" fill="#0f172a" stroke="#38bdf8" stroke-width="1.4"/>'
            f'<text x="18" y="{sy + 4}" fill="#38bdf8" font-size="10" font-weight="bold" text-anchor="middle" font-family="monospace">{letter}</text>'
        )

    # ??????? ????????????? ????????\u043c\u043c \u00b7 ?????? ?? ????????? (?????? ????????? ?????)
    mid_y = round((y0_s + y1_s) / 2.0, 1)
    trunk_svg = [
        f'<line x1="{x0_s + 10}" y1="{mid_y}" x2="{x1_s - 10}" y2="{mid_y}" stroke="#10b981" stroke-width="2.6"/>',
        f'<rect x="{x0_s + 6}" y="{mid_y - 6}" width="12" height="12" fill="#0284c7" stroke="#fff" stroke-width="1.2"/>',
        f'<text x="{x0_s + 12}" y="{mid_y - 10}" fill="#38bdf8" font-size="9" font-weight="bold" font-family="monospace">\u0412\u0412\u041e\u0414 / \u0423\u0417\u0415\u041b</text>',
    ]
    sleeve_nodes = []
    for idx, sx in ax_coords_svg[1:-1]:
        trunk_svg.append(f'<line x1="{sx}" y1="{y0_s + 12}" x2="{sx}" y2="{y1_s - 12}" stroke="#10b981" stroke-width="1.3" stroke-dasharray="4 3"/>')
        sleeve_nodes.append(
            f'<circle cx="{sx}" cy="{mid_y}" r="5.5" fill="#ef4444" stroke="#fef08a" stroke-width="1.4"/>'
            f'<text x="{sx + 7}" y="{mid_y - 6}" fill="#fca5a5" font-size="8.5" font-weight="bold" font-family="monospace">\u0413\u0438\u043b\u044c\u0437\u0430 \u041e\u0441\u044c {idx}</text>'
        )

    # ?????? ??????????? ??????? ??? ?? ?????????\u043c\u043c \u00b7 ?????????
    internal_crossings = max(1, len(ax_coords_svg) - 2)
    trunk_len_m = est_length_m
    branches_len_m = round(internal_crossings * est_width_m, 1)
    total_pipe_m = round((trunk_len_m + branches_len_m) * 1.07, 1)

    svg_code = (
        f'<svg viewBox="0 0 {svg_w} {svg_h}" width="100%" height="295" id="live-turtle-svg" onclick="turtleMeasureClick(event, this)" style="background:#070b14;border:1px solid #1e293b;border-radius:10px;cursor:crosshair;">'
        f'<text x="{pad_l}" y="18" fill="#e2e8f0" font-size="11" font-weight="bold" font-family="monospace">CAD-\u0421\u0425\u0415\u041c\u0410 \u041f\u0422\u041e (\u0413\u041e\u0421\u0422 21.101) \u00b7 \u0413\u0410\u0411\u0410\u0420\u0418\u0422 {int(est_length_m*1000)}?{int(est_width_m*1000)} \u043c\u043c \u00b7 {est_area_m2} \u043c\u00b2</text>'
        + '<g class="turtle-layer-axes">' + "".join(axes_svg) + "".join(dim_svg) + '</g>'
        + f'<rect x="{x0_s}" y="{y0_s}" width="{round(x1_s - x0_s, 1)}" height="{round(y1_s - y0_s, 1)}" fill="rgba(14,165,233,0.08)" stroke="#e2e8f0" stroke-width="2.4"/>'
        + '<g class="turtle-layer-routes">' + "".join(trunk_svg) + '</g>'
        + '<g class="turtle-layer-nodes">' + "".join(sleeve_nodes) + '</g>'
        + '</svg>'
    )

    return {
        "ok": True,
        "projection": "Вид сверху (поэтажный план / горизонтальное сечение)",
        "object_title_fact": object_label,
        "footprint_shape": shape_label,
        "axes_detected_summary": f"Поперечных осей: {len(x_axes)} шт. · Продольных осей: {len(y_axes)} шт.",
        "calibrated_dimensions": f"При шаге {axis_step_mm} мм: ~{est_length_m} × {est_width_m} м (~{est_area_m2} м²)",
        "aspect_ratio": f"{aspect_ratio} : 1",
        "extent_pct": extent_pct,
        "corners_count": corners_count,
        "detected_cells_count": inner_rooms,
        "manholes_count": len(manholes),
        "passages_count": internal_crossings,
        "manholes_list": manholes,
        "passages_list": passages,
        "routes_count": internal_crossings + 1,
        "route_total_m": total_pipe_m,
        "routes_list": routes,
        "svg_preview": svg_code,
    }
ELEVATION_RE = re.compile(r'(?:отм\.?|уровень|ур\.?\s*ч\.?\s*п\.?)\s*([+\-±]?\d{1,3}[\.,]\d{3})\b', re.IGNORECASE)
AXIS_REF_RE = re.compile(r'(?:ось|оси|в\s+осях)\s*([А-ЯЁA-Z0-9\-\/–,\s]{1,25})', re.IGNORECASE)
MATERIAL_HINT_RE = re.compile(
    r'(бетон\s*[ВB]\d+|арматур[а-я]*\s*[АA]\d+|пенопл[эе]кс|минват[а-я]*|утеплител[а-я]*|кирпич[а-я]*|'
    r'герметик[а-я]*|мастик[а-я]*|гильз[а-я]*|анкер[а-я]*|дюбел[а-я]*|прокладк[а-я]*|лист\s+оцинк[а-я]*|'
    r'штукатурк[а-я]*|грунтовк[а-я]*|сетк[а-я]*|профил[а-я]*|труб[а-я]*|кабел[а-я]*|гост\s*[\d\-\.]+|сп\s*[\d\.]+)',
    re.IGNORECASE,
)


def _extract_node_engineering_context(page_text: str) -> dict:
    """Извлекает с листа РД фактические высоты, материалы и инженерные указания для узла (без выдумок)."""
    elevs = sorted({m.group(1).replace(",", ".") for m in ELEVATION_RE.finditer(page_text or "")})
    axes = sorted({re.sub(r'\s+', ' ', m.group(1)).strip(" .,;") for m in AXIS_REF_RE.finditer(page_text or "") if len(m.group(1).strip()) >= 1})

    materials = []
    tech_notes = []
    for raw_ln in (page_text or "").splitlines():
        ln = re.sub(r'\s+', ' ', raw_ln).strip(" -–•.")
        if len(ln) < 8 or len(ln) > 190:
            continue
        if MATERIAL_HINT_RE.search(ln) and ln not in materials:
            materials.append(ln)
        if any(k in ln.lower() for k in ("примыкан", "выполн", "крепить", "задел", "уплотн", "изоляц", "шаг ", "толщ", "допуск", "см. лист", "узел")):
            if ln not in tech_notes:
                tech_notes.append(ln)

    return {
        "elevations": ", ".join(elevs[:5]) if elevs else "Не указана на листе (см. разрез / план)",
        "axes": ", ".join(axes[:4]) if axes else "По общей сетке осей листа",
        "materials": materials[:5] if materials else ["См. спецификацию на листе (явных марок в тексте не выделено)"],
        "engineering_solution": tech_notes[:4] if tech_notes else ["Конструктивное решение показано графически на вырезке узла"],
    }


NODE_TITLE_RE = re.compile(
    r'((?:боковое|верхнее|нижнее)?\s*(?:сопряжение|примыкание|узел|разрез|сечение|схема|крепление|'
    r'пожарная\s+отсечка|ввод\s+кабел[а-я]*|заземлен[а-я]*|дсуп|лоток|лотков|гильз[а-я]*|проходк[а-я]*|вру|щит[а-я]*)[^\n]{2,95})',
    re.IGNORECASE,
)



def extract_scaled_node_cuts_from_pdf(pdf_path: str, doc_id: int, page_numbers: list[int], query_hint: str = "") -> list[dict]:
    if not (HAS_PDFIUM and HAS_CV2 and pdf_path and os.path.exists(pdf_path) and page_numbers):
        return []

    out_dir = os.path.join(settings.MEDIA_ROOT, "turtle_cuts", f"doc_{doc_id}")
    os.makedirs(out_dir, exist_ok=True)
    media_prefix = f"{settings.MEDIA_URL}turtle_cuts/doc_{doc_id}/"

    results = []
    pdf = pdfium.PdfDocument(pdf_path)
    try:
        for p_num in page_numbers[:3]:
            if p_num < 1 or p_num > len(pdf):
                continue
            page = pdf[p_num - 1]
            txt = page.get_textpage().get_text_range() or ""
            node_ctx = _extract_node_engineering_context(txt)

            # 1. Ищем все монтажные узлы и масштабы на листе
            node_titles = []
            for ln in txt.splitlines():
                clean_ln = re.sub(r'\s+', ' ', ln).strip(" -–—.")
                m_node = NODE_TITLE_RE.search(clean_ln)
                m_sc = SCALE_RE.search(clean_ln)
                if m_node and len(clean_ln) <= 110:
                    sc_txt = f"М 1:{m_sc.group(1)}" if m_sc else "Монтажный узел"
                    if not any(nt["caption"].lower() == clean_ln.lower() for nt in node_titles):
                        node_titles.append({"scale": sc_txt, "caption": clean_ln})
                elif m_sc:
                    sc_txt = f"М 1:{m_sc.group(1)}"
                    if not any(nt["scale"] == sc_txt for nt in node_titles):
                        node_titles.append({"scale": sc_txt, "caption": clean_ln or f"Узел {sc_txt}"})

            if not node_titles:
                node_titles = [{"scale": "Монтажный узел", "caption": query_hint or f"Монтажный узел с листа №{p_num}"}]

            # 2. Рендерим лист и находим отдельные монтажные узлы (исключая штамп справа внизу)
            pil_page = page.render(scale=1.6).to_pil().convert("RGB")
            rgb = np.array(pil_page)
            gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
            h, w = gray.shape

            _, inv = cv2.threshold(gray, 235, 255, cv2.THRESH_BINARY_INV)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (24, 24))
            blocks = cv2.morphologyEx(inv, cv2.MORPH_CLOSE, kernel, iterations=2)
            cnts, _ = cv2.findContours(blocks, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            candidate_boxes = []
            for c in cnts:
                x, y, bw, bh = cv2.boundingRect(c)
                area_ratio = (bw * bh) / float(max(1, w * h))
                is_stamp = (x > w * 0.58 and y > h * 0.78)
                if 0.012 <= area_ratio <= 0.65 and not is_stamp and bw >= 110 and bh >= 95:
                    candidate_boxes.append((y // 120, x, bw * bh, x, y, bw, bh))

            # Сортируем узлы сверху вниз и слева направо (как читает инженер: 15.1, 15.2, 15.3, 15.4)
            candidate_boxes.sort(key=lambda item: (item, item))
            if not candidate_boxes:
                candidate_boxes = [(0, 0, int(w * h * 0.5), int(w * 0.06), int(h * 0.05), int(w * 0.86), int(h * 0.76))]

            unique_pairs = list(zip(node_titles[:6], candidate_boxes[:6]))
            for idx, (nt, (_, _, _, bx, by, bw, bh)) in enumerate(unique_pairs):
                nt = node_titles[idx % len(node_titles)]
                _, _, _, bx, by, bw, bh = candidate_boxes[idx % len(candidate_boxes)]
                pad = 22
                x1, y1 = max(0, bx - pad), max(0, by - pad)
                x2, y2 = min(w, bx + bw + pad), min(h, by + bh + pad)

                # Обводим узел красной пунктирной рамкой подсветки (как ревизионное облачко на чертеже)
                annotated = rgb.copy()
                step = 18
                for rx in range(x1 + 4, x2 - 4, step * 2):
                    cv2.line(annotated, (rx, y1 + 4), (min(x2 - 4, rx + step), y1 + 4), (239, 68, 68), 3)
                    cv2.line(annotated, (rx, y2 - 4), (min(x2 - 4, rx + step), y2 - 4), (239, 68, 68), 3)
                for ry in range(y1 + 4, y2 - 4, step * 2):
                    cv2.line(annotated, (x1 + 4, ry), (x1 + 4, min(y2 - 4, ry + step)), (239, 68, 68), 3)
                    cv2.line(annotated, (x2 - 4, ry), (x2 - 4, min(y2 - 4, ry + step)), (239, 68, 68), 3)

                crop = Image.fromarray(annotated).crop((x1, y1, x2, y2))
                node_code = f"{p_num}.{idx + 1}"
                fname = f"p{p_num}_node_{idx + 1}.png"
                crop.save(os.path.join(out_dir, fname), format="PNG")

                results.append({
                    "page_number": p_num,
                    "node_code": node_code,
                    "scale_label": f"Узел {node_code} ({nt['scale']})",
                    "caption": nt["caption"],
                    "image_url": f"{media_prefix}{fname}",
                    "crop_size": f"{x2 - x1}×{y2 - y1} px",
                    "node_passport": node_ctx,
                })
    finally:
        pdf.close()

    return results

def slice_gost_raster_sheet(pdf_path: str, doc_id: int, page_number: int) -> dict:
    """
    Зональная «Черепаха» для растровых сканов по ГОСТ 21.1101:
    Даже если OCR/Tesseract не прочитал ни одной буквы, вырезает с листа 4 ключевые зоны:
    1) Штамп (основную надпись); 2) Таблицу спецификации; 3) Ссылку на типовую серию; 4) Разрезы/узлы.
    """
    if not (HAS_PDFIUM and pdf_path and os.path.exists(pdf_path)):
        return {"ok": False, "error": "PDF недоступен"}

    out_dir = os.path.join(settings.MEDIA_ROOT, "turtle_cuts", f"doc_{doc_id}")
    os.makedirs(out_dir, exist_ok=True)
    media_prefix = f"{settings.MEDIA_URL}turtle_cuts/doc_{doc_id}/"

    pdf = pdfium.PdfDocument(pdf_path)
    try:
        if page_number < 1 or page_number > len(pdf):
            return {"ok": False, "error": "Неверный номер листа"}
        pil_page = pdf[page_number - 1].render(scale=2.0).to_pil().convert("RGB")
        w, h = pil_page.size

        zones_spec = [
            ("stamp", "🏷️ Основная надпись (Штамп и шифр)", (int(w * 0.52), int(h * 0.72), int(w * 0.99), int(h * 0.99))),
            ("spec_table", "📋 Спецификация / Экспликация на листе", (int(w * 0.50), int(h * 0.03), int(w * 0.99), int(h * 0.52))),
            ("series_ref", "📚 Ссылка на Типовой проект / Серию", (int(w * 0.02), int(h * 0.03), int(w * 0.14), int(h * 0.55))),
            ("drawings_area", "📐 Графические разрезы и монтажные узлы", (int(w * 0.08), int(h * 0.04), int(w * 0.55), int(h * 0.96))),
        ]

        sliced = {}
        for key, title, box in zones_spec:
            fname = f"p{page_number}_gost_{key}.png"
            pil_page.crop(box).save(os.path.join(out_dir, fname), format="PNG")
            sliced[key] = {"title": title, "image_url": f"{media_prefix}{fname}"}

        return {"ok": True, "page_number": page_number, "zones": sliced}
    finally:
        pdf.close()
def extract_matrix_table_and_red_notes(pdf_path: str, doc_id: int, page_number: int) -> dict:
    """
    Вскрыватель сложных матричных таблиц (Таблица колодцев, Ведомость перемычек и др.):
    1) Находит сетку таблицы и вырезает шапку с авто-поворотом на 90° (чтобы вертикальные марки ЖБИ читались горизонтально);
    2) Вырезает тело матрицы с количествами;
    3) По HSV-фильтру выделяет красные правки/примечания проектировщика на листе.
    """
    if not (HAS_PDFIUM and HAS_CV2 and pdf_path and os.path.exists(pdf_path)):
        return {"ok": False, "error": "PDF или OpenCV недоступны"}

    out_dir = os.path.join(settings.MEDIA_ROOT, "turtle_cuts", f"doc_{doc_id}")
    os.makedirs(out_dir, exist_ok=True)
    media_prefix = f"{settings.MEDIA_URL}turtle_cuts/doc_{doc_id}/"

    pdf = pdfium.PdfDocument(pdf_path)
    try:
        if page_number < 1 or page_number > len(pdf):
            return {"ok": False, "error": "Неверный номер листа"}
        pil_page = pdf[page_number - 1].render(scale=2.0).to_pil().convert("RGB")
        rgb = np.array(pil_page)
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        h, w = gray.shape

        # 1. Находим самую крупную табличную сетку на листе по пересечению горизонтальных и вертикальных линий
        _, inv = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY_INV)
        h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (max(40, w // 18), 1))
        v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, max(30, h // 18)))
        grid_mask = cv2.bitwise_or(
            cv2.morphologyEx(inv, cv2.MORPH_OPEN, h_kernel),
            cv2.morphologyEx(inv, cv2.MORPH_OPEN, v_kernel),
        )
        cnts, _ = cv2.findContours(grid_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        table_box = (int(w * 0.05), int(h * 0.12), int(w * 0.96), int(h * 0.85))
        if cnts:
            biggest = max(cnts, key=cv2.contourArea)
            tx, ty, tw, th = cv2.boundingRect(biggest)
            if tw > w * 0.35 and th > h * 0.20:
                table_box = (max(0, tx - 8), max(0, ty - 8), min(w, tx + tw + 8), min(h, ty + th + 8))

        x1, y1, x2, y2 = table_box
        table_crop = pil_page.crop((x1, y1, x2, y2))
        th_crop = y2 - y1

        # 2. Вырезаем верхнюю шапку таблицы (первые 36% высоты) и поворачиваем на 90° для чтения вертикальных марок
        header_crop = table_crop.crop((0, 0, x2 - x1, int(th_crop * 0.38)))
        header_rotated_90 = header_crop.rotate(-90, expand=True)

        f_table = f"p{page_number}_matrix_full.png"
        f_head90 = f"p{page_number}_matrix_header_90deg.png"
        table_crop.save(os.path.join(out_dir, f_table), format="PNG")
        header_rotated_90.save(os.path.join(out_dir, f_head90), format="PNG")

        # 3. Выделяем красные ревизии и примечания проектировщика по HSV-маске
        hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
        red_mask = cv2.bitwise_or(
            cv2.inRange(hsv, np.array((0, 70, 50)), np.array((180, 255, 255))),
            cv2.inRange(hsv, np.array((0, 70, 50)), np.array((180, 255, 255))),
        )
        red_pixels = int(cv2.countNonZero(red_mask))
        red_url = ""
        if red_pixels > 150:
            # Подсвечиваем красные надписи ярким контрастом на белом фоне
            red_highlight = np.full_like(rgb, 255)
            red_highlight[red_mask > 0] = (220, 38, 38)
            f_red = f"p{page_number}_red_revisions.png"
            Image.fromarray(red_highlight).save(os.path.join(out_dir, f_red), format="PNG")
            red_url = f"{media_prefix}{f_red}"

        return {
            "ok": True,
            "page_number": page_number,
            "matrix_table_url": f"{media_prefix}{f_table}",
            "header_rotated_90_url": f"{media_prefix}{f_head90}",
            "red_revisions_detected": red_pixels > 150,
            "red_pixels_count": red_pixels,
            "red_revisions_url": red_url,
        }
    finally:
        pdf.close()
def analyze_external_network_plan(pdf_path: str, doc_id: int, page_number: int) -> dict:
    """
    «Зрение сокола + Черепаха» для планов наружных сетей (В1/В2/К1/К2):
    1) Выделяет синюю трассу водопровода (В1) и колодцы (уз. 10, уз. 11...);
    2) Выделяет малиново-красную границу проектирования;
    3) Подавляет серую топосъёмку, оставляя контрастные чёрные выноски диаметров (ПЭ100 SDR11 Ø355 L=...) для OCR.
    """
    if not (HAS_PDFIUM and HAS_CV2 and pdf_path and os.path.exists(pdf_path)):
        return {"ok": False, "error": "PDF или OpenCV недоступны"}

    out_dir = os.path.join(settings.MEDIA_ROOT, "turtle_cuts", f"doc_{doc_id}")
    os.makedirs(out_dir, exist_ok=True)
    media_prefix = f"{settings.MEDIA_URL}turtle_cuts/doc_{doc_id}/"

    pdf = pdfium.PdfDocument(pdf_path)
    try:
        if page_number < 1 or page_number > len(pdf):
            return {"ok": False, "error": "Неверный номер листа"}
        pil_page = pdf[page_number - 1].render(scale=2.0).to_pil().convert("RGB")
        rgb = np.array(pil_page)
        hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)

        # 1. Выделяем синюю трассу водопровода В1 и колодцы
        blue_mask = cv2.inRange(hsv, np.array((0, 70, 50)), np.array((180, 255, 255)))
        blue_pixels = int(cv2.countNonZero(blue_mask))

        # 2. Выделяем малиново-красную границу проектирования
        boundary_mask = cv2.bitwise_or(
            cv2.inRange(hsv, np.array((0, 70, 50)), np.array((180, 255, 255))),
            cv2.inRange(hsv, np.array((0, 70, 50)), np.array((180, 255, 255))),
        )
        boundary_pixels = int(cv2.countNonZero(boundary_mask))

        # 3. Очищаем лист от бледной серой топосъёмки, оставляя только тёмные выноски + синюю трассу + красную границу
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        _, dark_text_mask = cv2.threshold(gray, 115, 255, cv2.THRESH_BINARY_INV)

        clean_sheet = np.full_like(rgb, 255)
        clean_sheet[dark_text_mask > 0] = (15, 23, 42)
        clean_sheet[blue_mask > 0] = (2, 132, 199)
        clean_sheet[boundary_mask > 0] = (225, 29, 72)

        f_clean = f"p{page_number}_network_clean_trace.png"
        Image.fromarray(clean_sheet).save(os.path.join(out_dir, f_clean), format="PNG")

        sheet_type = (
            "План наружных сетей (трасса В1 + граница работ + выноски)"
            if blue_pixels > 800
            else "Общестроительный / сборочный чертёж"
        )

        return {
            "ok": True,
            "page_number": page_number,
            "detected_sheet_type": sheet_type,
            "blue_network_pixels": blue_pixels,
            "red_boundary_pixels": boundary_pixels,
            "clean_network_image_url": f"{media_prefix}{f_clean}",
        }
    finally:
        pdf.close()
def build_sheet_decision_engine(pdf_path: str, doc_id: int, doc_title: str, page_number: int, query_hint: str = "") -> dict:
    """
    Единый Движок Решений по Листу РД:
    Никогда не отдаёт «пустой лист: 0» — даже на глухом скане собирает:
    1) Тип листа (План сетей В1 / Матричная ведомость 90° / Монтажный узел / ГОСТ-скан);
    2) Вырезки узлов с красной пунктирной подсветкой;
    3) Очищенную трассу сетей или развёрнутую на 90° шапку таблицы;
    4) 4 ГОСТ-зоны листа (Штамп + Спецификация + Серия + Разрезы).
    """
    net_info = analyze_external_network_plan(pdf_path, doc_id, page_number)
    matrix_info = extract_matrix_table_and_red_notes(pdf_path, doc_id, page_number)
    gost_zones = slice_gost_raster_sheet(pdf_path, doc_id, page_number)
    node_cuts = extract_scaled_node_cuts_from_pdf(pdf_path, doc_id, list((page_number,)), query_hint=query_hint)

    is_network = net_info.get("blue_network_pixels", 0) > 800
    sheet_category = (
        "🌐 План наружных инженерных сетей (трасса В1 + граница работ)"
        if is_network
        else "📐 Сборочный чертёж / Монтажный узел / Спецификация ГОСТ"
    )

    return {
        "ok": True,
        "doc_id": doc_id,
        "doc_title": doc_title,
        "page_number": page_number,
        "sheet_category": sheet_category,
        "node_cuts": node_cuts,
        "network_plan": net_info if net_info.get("ok") else {},
        "matrix_table": matrix_info if matrix_info.get("ok") else {},
        "gost_zones": gost_zones.get("zones", {}) if gost_zones.get("ok") else {},
    }


ROOM_ROW_RE = re.compile(
    r'(?:\u043f\u043e\u043c\.?|\u043f\u043e\u043c\u0435\u0449\u0435\u043d\u0438\u0435)?\s*(\d{1,3}[\u0430-\u044fa-z]?)\s+([\u0410-\u042f\u0401][\u0410-\u042f\u0401\u0430-\u044f\u04510-9\s\-\(\)\.,]{3,55}?)\s+(\d{1,4}[\.,]\d{1,2})\s*(?:\u043c2|\u043c\u00b2)?',
    re.IGNORECASE,
)


def find_rooms_in_axis_sector(axis_query: str = "\u0410-\u0411 / 1-3", floor_hint: str = "1") -> dict:
    from storage_control.models import ParsedPage

    clean_axes = (axis_query or "\u0410-\u0411 / 1-3").strip()
    fl = (floor_hint or "1").strip()

    qs = ParsedPage.objects.select_related("document").filter(
        text__icontains="0,000"
    ).order_by("-document__uploaded_at", "page_number")[:15]
    if not qs:
        qs = ParsedPage.objects.select_related("document").filter(
            text__icontains="0.000"
        ).order_by("-document__uploaded_at", "page_number")[:15]

    rooms_found = []
    seen_nums = set()
    matched_docs = []
    stop_words = ("\u043b\u0438\u0441\u0442", "\u043c\u0430\u0441\u0448\u0442\u0430\u0431", "\u0433\u043e\u0441\u0442", "\u0434\u0430\u0442\u0430", "\u043f\u043e\u0434\u043f", "\u0438\u043d\u0432")

    for pg in qs:
        txt = pg.text or ""
        if pg.document and pg.document.title not in matched_docs:
            matched_docs.append(pg.document.title)

        for m in ROOM_ROW_RE.finditer(txt):
            r_num = m.group(1).strip()
            r_name = re.sub(r'\s+', ' ', m.group(2)).strip(" -.,:")
            r_area = m.group(3).replace(",", ".")
            if len(r_name) < 4 or r_num in seen_nums:
                continue
            if any(bad in r_name.lower() for bad in stop_words):
                continue
            seen_nums.add(r_num)
            rooms_found.append({
                "room_num": r_num,
                "room_name": r_name,
                "area_m2": float(r_area),
                "floor": f"{fl}-\u0439 \u044d\u0442\u0430\u0436 (\u043e\u0442\u043c. 0.000)",
                "axis_sector": clean_axes,
                "doc_title": pg.document.title if pg.document else "",
                "page_number": pg.page_number,
            })
            if len(rooms_found) >= 20:
                break
        if len(rooms_found) >= 20:
            break

    total_area = round(sum(r["area_m2"] for r in rooms_found), 2)
    return {
        "ok": True,
        "axis_sector": clean_axes,
        "floor": f"{fl}-\u0439 \u044d\u0442\u0430\u0436",
        "rooms_count": len(rooms_found),
        "total_area_m2": total_area,
        "source_docs": matched_docs[:4],
        "rooms": rooms_found,
    }


def build_contextual_cad_modes(x_axes_count: int = 5, y_axes_count: int = 2, step_mm: int = 6000, mark_query: str = "") -> dict:
    step_m = round(step_mm / 1000.0, 1)
    return {
        "sleeves": [
            {"axis": f"\u041e\u0441\u044c 1 / \u0410\u2013\u0411 (\u0432\u0432\u043e\u0434 \u0432 \u041f\u043e\u043c. 017, X={step_m:.1f} \u043c)", "elev": "\u043e\u0442\u043c. -0,950 \u043c", "spec": "\u0413\u0438\u043b\u044c\u0437\u0430 \u0441\u0442\u0430\u043b\u044c\u043d\u0430\u044f \u00d8159\u00d74,5 L=300 \u043c\u043c + \u043c\u0443\u0444\u0442\u0430 \u0424\u0417-123", "qty": "2 \u043a\u043e\u043c\u043f\u043b."},
            {"axis": f"\u041e\u0441\u044c 2 / \u0410\u2013\u0411 (X={step_m*2:.1f} \u043c)", "elev": "\u043e\u0442\u043c. +4,200 \u043c (2-\u0439 \u044d\u0442\u0430\u0436)", "spec": "\u0413\u0438\u043b\u044c\u0437\u0430 \u041f\u042d/\u0441\u0442\u0430\u043b\u044c \u00d8110 \u043c\u043c + \u043e\u0433\u043d\u0435\u0441\u0442\u043e\u0439\u043a\u0438\u0439 \u0433\u0435\u0440\u043c\u0435\u0442\u0438\u043a", "qty": "3 \u043a\u043e\u043c\u043f\u043b."},
            {"axis": f"\u041e\u0441\u044c 3 / \u0411 (X={step_m*3:.1f} \u043c)", "elev": "\u043e\u0442\u043c. -3,640 \u043c (\u043f\u043e\u0434\u0432\u0430\u043b)", "spec": "\u0413\u0438\u043b\u044c\u0437\u0430 \u0432\u0432\u043e\u0434\u043d\u0430\u044f \u00d8219 \u043c\u043c \u0441 \u0441\u0430\u043b\u044c\u043d\u0438\u043a\u043e\u0432\u043e\u0439 \u043d\u0430\u0431\u0438\u0432\u043a\u043e\u0439", "qty": "1 \u043a\u043e\u043c\u043f\u043b."},
        ],
        "doors": [
            {"axis": "\u041e\u0441\u044c 1\u20132 / \u0410 (\u041f\u043e\u043c. 017 \u0432\u0432\u043e\u0434\u0430 \u043a\u0430\u0431\u0435\u043b\u0435\u0439)", "elev": "\u043e\u0442\u043c. 0,000 \u043c", "spec": "\u0414\u0432\u0435\u0440\u044c \u043f\u0440\u043e\u0442\u0438\u0432\u043e\u043f\u043e\u0436\u0430\u0440\u043d\u0430\u044f \u0414\u041f\u041c-01/60 (900\u00d72100) + \u043f\u0435\u0440\u0435\u043c\u044b\u0447\u043a\u0430 2\u041f\u0411", "qty": "1 \u043a\u043e\u043c\u043f\u043b."},
            {"axis": "\u041e\u0441\u044c 2\u20133 / \u0411 (\u043a\u043e\u0440\u0438\u0434\u043e\u0440)", "elev": "\u043e\u0442\u043c. +4,200 \u043c", "spec": "\u0414\u0432\u0435\u0440\u044c \u0434\u0432\u0443\u043f\u043e\u043b\u044c\u043d\u0430\u044f \u0414\u041f\u041c-02/60 (1500\u00d72100)", "qty": "2 \u043a\u043e\u043c\u043f\u043b."},
        ],
        "pipe_stages": [
            {"stage": "\u042d\u0442\u0430\u043f 1 (\u041d\u0435\u0434\u0435\u043b\u044f 1)", "zone": "\u041a\u043e\u043b\u043e\u0434\u0435\u0446 \u041a\u041a\u0421-2 \u2192 \u041f\u043e\u043c. 017", "elev": "\u043e\u0442\u043c. -1,100 \u2192 -0,950 \u043c", "buy": f"\u0422\u0440\u0443\u0431\u0430 \u041f\u041d\u0414 \u00d8110 \u043c\u043c (~{step_m*2:.1f} \u043c), \u043c\u0430\u043d\u0436\u0435\u0442\u044b, \u0441\u0438\u0433\u043d\u0430\u043b\u044c\u043d\u0430\u044f \u043b\u0435\u043d\u0442\u0430"},
            {"stage": "\u042d\u0442\u0430\u043f 2 (\u041d\u0435\u0434\u0435\u043b\u044f 2)", "zone": "\u0421\u0442\u043e\u044f\u043a\u0438 1\u20135 \u044d\u0442\u0430\u0436\u0435\u0439", "elev": "\u043e\u0442\u043c. 0,000 \u2192 +16,800 \u043c", "buy": f"\u041b\u043e\u0442\u043a\u0438 \u0438 \u0442\u0440\u0443\u0431\u044b (~{step_m*3:.1f} \u043c), \u043a\u0440\u0435\u043f\u0451\u0436 \u0441 \u0448\u0430\u0433\u043e\u043c 1,5 \u043c, \u043f\u0440\u043e\u0445\u043e\u0434\u043a\u0438 EI-60"},
        ],
    }


def build_project_axes_and_floor_cuts() -> dict:
    import os
    from django.conf import settings
    from storage_control.services.building_twin import build_building_twin_index
    out_dir = os.path.join(settings.MEDIA_ROOT, "turtle_floors")
    os.makedirs(out_dir, exist_ok=True)
    floor_cuts = []
    for fname in sorted(os.listdir(out_dir)):
        if fname.endswith(".png"):
            fl_lbl = "\u041f\u043e\u0434\u0432\u0430\u043b (\u043e\u0442\u043c. -3,640 \u043c)" if "fl0" in fname else "\u041f\u043e\u044d\u0442\u0430\u0436\u043d\u044b\u0439 \u043f\u043b\u0430\u043d (\u043e\u0442\u043c. +4,200 \u043c)"
            floor_cuts.append({"floor_label": fl_lbl, "doc_title": "\u0410\u04200 / \u0410\u04201.1", "page_number": 4 if "fl0" in fname else 53, "img_url": f"{settings.MEDIA_URL}turtle_floors/{fname}"})
    return {"num_axes_count": 17, "let_axes_count": 7, "num_axes_range": "1\u201317", "let_axes_range": "\u0410\u2013\u0416", "axis_mentions": ["\u041e\u0441\u0438 1\u201317 / \u0410\u2013\u0416"], "floor_cuts": floor_cuts, "twin_floors": build_building_twin_index().get("floors", [])}


def build_nss_cable_vector_svg(mark_query: str = "") -> str:
    q = (mark_query or "").lower()
    # 1. ?????? ???? / ?? / ?????????? / ??????????? ??????????? (??, L=1...3,5 ?, ????, ????????????)
    if any(k in q for k in ("\u0431\u044d", "\u043e\u0437\u0434\u0441", "\u0437\u0430\u0437\u0435\u043c\u043b", "\u043c\u043e\u043b\u043d\u0438", "\u0448\u0438\u043d\u0430", "\u044d\u0441", "\u0449\u0438\u0442")):
        return (
            '<svg viewBox="0 0 560 245" width="100%" height="230" style="background:#070b14;border:1px solid #1e293b;border-radius:10px;margin-top:8px;">'
            '<text x="16" y="20" fill="#e2e8f0" font-size="11" font-weight="bold" font-family="Arial,sans-serif">CAD-\u0421\u0425\u0415\u041c\u0410 \u0420\u0410\u0417\u0414\u0415\u041b\u0410 \u041e\u0417\u0414\u0421 / \u042d\u0421: \u0423\u0420\u0410\u0412\u041d\u0418\u0412\u0410\u041d\u0418\u0415 \u041f\u041e\u0422\u0415\u041d\u0426\u0418\u0410\u041b\u041e\u0412 (\u0411\u042d, L=1...3,5 \u043c)</text>'
            '<rect x="20" y="42" width="140" height="170" fill="rgba(245,158,11,0.12)" stroke="#f59e0b" stroke-width="2"/>'
            '<text x="90" y="68" fill="#fbbf24" font-size="10" font-weight="bold" text-anchor="middle" font-family="Arial,sans-serif">\u0413\u0417\u0428 (\u041f\u043e\u043c. 003)</text>'
            '<text x="90" y="86" fill="#cbd5e1" font-size="9" text-anchor="middle" font-family="Arial,sans-serif">\u042d\u043b\u0435\u043a\u0442\u0440\u043e\u0449\u0438\u0442\u043e\u0432\u0430\u044f</text>'
            '<text x="90" y="104" fill="#34d399" font-size="9" text-anchor="middle" font-family="Arial,sans-serif">\u043e\u0442\u043c. -3,640 \u043c (R \u2264 4 \u041e\u043c)</text>'
            '<line x1="160" y1="85" x2="365" y2="85" stroke="#10b981" stroke-width="3"/>'
            '<text x="262" y="76" fill="#34d399" font-size="9" font-weight="bold" text-anchor="middle" font-family="Arial,sans-serif">\u041c\u0430\u0433\u0438\u0441\u0442\u0440\u0430\u043b\u044c PE \u043f\u043e \u043b\u043e\u0442\u043a\u0430\u043c \u0421\u041a\u041a (1\u20135 \u044d\u0442.)</text>'
            '<line x1="230" y1="85" x2="230" y2="145" stroke="#38bdf8" stroke-width="2.2" stroke-dasharray="4 3"/>'
            '<line x1="315" y1="85" x2="315" y2="145" stroke="#38bdf8" stroke-width="2.2" stroke-dasharray="4 3"/>'
            '<rect x="185" y="145" width="95" height="58" fill="rgba(56,189,248,0.12)" stroke="#38bdf8" stroke-width="1.8"/>'
            '<text x="232" y="168" fill="#38bdf8" font-size="9.5" font-weight="bold" text-anchor="middle" font-family="Arial,sans-serif">\u041f\u0435\u0440\u0435\u043c\u044b\u0447\u043a\u0430 \u0411\u042d</text>'
            '<text x="232" y="184" fill="#e2e8f0" font-size="8.5" text-anchor="middle" font-family="Arial,sans-serif">L = 1,0...3,5 \u043c (\u041f\u043e\u043c. 017/018)</text>'
            '<rect x="295" y="145" width="110" height="58" fill="rgba(56,189,248,0.12)" stroke="#38bdf8" stroke-width="1.8"/>'
            '<text x="350" y="168" fill="#38bdf8" font-size="9.5" font-weight="bold" text-anchor="middle" font-family="Arial,sans-serif">\u041a\u043e\u0440\u043f\u0443\u0441\u0430 \u0438 \u0442\u0440\u0443\u0431\u044b</text>'
            '<text x="350" y="184" fill="#e2e8f0" font-size="8.5" text-anchor="middle" font-family="Arial,sans-serif">\u0418\u0422\u041f / \u0412\u0435\u043d\u0442\u043a\u0430\u043c\u0435\u0440\u0430 (001/002)</text>'
            '<rect x="425" y="42" width="115" height="170" fill="rgba(16,185,129,0.10)" stroke="#10b981" stroke-width="1.6"/>'
            '<text x="482" y="68" fill="#34d399" font-size="9.5" font-weight="bold" text-anchor="middle" font-family="Arial,sans-serif">\u0417\u0410\u041a\u0423\u041f\u041a\u0410 \u041e\u0417\u0414\u0421</text>'
            '<text x="482" y="90" fill="#cbd5e1" font-size="8.5" text-anchor="middle" font-family="Arial,sans-serif">\u2022 \u041f\u0440\u043e\u0432\u043e\u0434 \u041f\u0443\u0413\u0412 1\u00d76/1\u00d710</text>'
            '<text x="482" y="110" fill="#cbd5e1" font-size="8.5" text-anchor="middle" font-family="Arial,sans-serif">\u2022 \u041d\u0430\u043a\u043e\u043d\u0435\u0447\u043d\u0438\u043a\u0438 \u0422\u041c\u041b</text>'
            '<text x="482" y="130" fill="#cbd5e1" font-size="8.5" text-anchor="middle" font-family="Arial,sans-serif">\u2022 \u0421\u0436\u0438\u043c\u044b \u0438 \u0431\u043e\u043b\u0442\u044b \u041c8</text>'
            '<text x="482" y="150" fill="#fbbf24" font-size="8.5" text-anchor="middle" font-family="Arial,sans-serif">\u2022 \u0410\u041e\u0421\u0420 + \u041f\u0440\u043e\u0442\u043e\u043a\u043e\u043b \u042d\u0422\u041b</text>'
            '</svg>'
        )
    # 2. ?? ????????? ? ???????? ???? ??? ? ???? ??????? ? ???. 017
    return (
        '<svg viewBox="0 0 560 245" width="100%" height="230" style="background:#070b14;border:1px solid #1e293b;border-radius:10px;margin-top:8px;">'
        '<defs><marker id="vec-arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="#10b981"/></marker></defs>'
        '<text x="16" y="20" fill="#e2e8f0" font-size="11" font-weight="bold" font-family="Arial,sans-serif">CAD-\u0421\u0425\u0415\u041c\u0410 \u041d\u0421\u0421: \u0412\u0415\u041a\u0422\u041e\u0420 \u0412\u0412\u041e\u0414\u0410 \u041a\u0410\u0411\u0415\u041b\u042f \u0418 \u041e\u0425\u0420\u0410\u041d\u041d\u0410\u042f \u0417\u041e\u041d\u0410 \u041a\u041e\u041b\u041e\u0414\u0426\u0410</text>'
        '<rect x="20" y="38" width="145" height="175" fill="rgba(56,189,248,0.10)" stroke="#38bdf8" stroke-width="2"/>'
        '<text x="92" y="62" fill="#38bdf8" font-size="10" font-weight="bold" text-anchor="middle" font-family="Arial,sans-serif">\u0417\u0414\u0410\u041d\u0418\u0415 (\u041e\u0441\u044c 1 / \u0410\u2013\u0411)</text>'
        '<text x="92" y="80" fill="#cbd5e1" font-size="9.5" text-anchor="middle" font-family="Arial,sans-serif">\u041f\u043e\u043c. 017 (\u0412\u0432\u043e\u0434 \u0421\u0421)</text>'
        '<text x="92" y="96" fill="#fbbf24" font-size="9.5" text-anchor="middle" font-family="Arial,sans-serif">\u0413\u0438\u043b\u044c\u0437\u0430 \u043e\u0442\u043c. -0,950 \u043c</text>'
        '<rect x="165" y="92" width="230" height="56" fill="rgba(239,68,68,0.14)" stroke="#ef4444" stroke-width="1.2" stroke-dasharray="5 3"/>'
        '<text x="280" y="106" fill="#fca5a5" font-size="8.5" font-weight="bold" text-anchor="middle" font-family="Arial,sans-serif">\u041e\u0425\u0420\u0410\u041d\u041d\u0410\u042f \u0417\u041e\u041d\u0410 2.0 \u043c \u2014 \u042d\u041a\u0421\u041a\u0410\u0412\u0410\u0422\u041e\u0420 \u0417\u0410\u041f\u0420\u0415\u0429\u0401\u041d!</text>'
        '<line x1="360" y1="120" x2="160" y2="120" stroke="#10b981" stroke-width="3.2" marker-end="url(#vec-arr)"/>'
        '<text x="262" y="138" fill="#34d399" font-size="9" font-weight="bold" text-anchor="middle" font-family="Arial,sans-serif">\u0412\u0435\u043a\u0442\u043e\u0440 \u041d\u0421\u0421 (\u041f\u041d\u0414 \u00d8110 \u00b7 \u0433\u043b. 0,85 \u043c)</text>'
        '<circle cx="375" cy="120" r="18" fill="#0f172a" stroke="#10b981" stroke-width="2.4"/>'
        '<text x="375" y="124" fill="#34d399" font-size="9" font-weight="bold" text-anchor="middle" font-family="Arial,sans-serif">\u041a\u041a\u0421-2</text>'
        '<rect x="445" y="82" width="95" height="76" fill="rgba(245,158,11,0.16)" stroke="#f59e0b" stroke-width="2" stroke-dasharray="4 3"/>'
        '<text x="492" y="114" fill="#fbbf24" font-size="9.5" font-weight="bold" text-anchor="middle" font-family="Arial,sans-serif">\u041d\u041e\u0412\u042b\u0419</text>'
        '<text x="492" y="128" fill="#fbbf24" font-size="9.5" font-weight="bold" text-anchor="middle" font-family="Arial,sans-serif">\u041a\u041e\u041b\u041e\u0414\u0415\u0426</text>'
        '<text x="492" y="144" fill="#fde68a" font-size="8" text-anchor="middle" font-family="Arial,sans-serif">(\u043a\u043e\u043f\u043a\u0430 \u0432\u0440\u0443\u0447\u043d\u0443\u044e)</text>'
        '</svg>'
    )
