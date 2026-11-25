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


def _cluster_coords(coords: list[float], min_gap: float) -> list[float]:
    if not coords:
        return []
    coords = sorted(coords)
    clusters = [[coords]]
    for c in coords[1:]:
        if abs(c - clusters[-1][-1]) <= min_gap:
            clusters[-1].append(c)
        else:
            clusters.append([c])
    return [round(sum(cl) / len(cl), 1) for cl in clusters]


def _detect_building_axes(gray_np: "np.ndarray", bx: int, by: int, bw: int, bh: int) -> tuple[list[float], list[float]]:
    edges = cv2.Canny(gray_np, 50, 150, apertureSize=3)
    min_v_len = max(35, int(bh * 0.28))
    min_h_len = max(35, int(bw * 0.28))
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=55, minLineLength=min(min_v_len, min_h_len), maxLineGap=14)

    v_xs, h_ys = [], []
    if lines is not None:
        for ln in lines:
            x1, y1, x2, y2 = ln
            dx, dy = abs(x2 - x1), abs(y2 - y1)
            if dx <= 6 and dy >= min_v_len:
                mx = (x1 + x2) / 2.0
                if bx - 10 <= mx <= bx + bw + 10:
                    v_xs.append(mx)
            elif dy <= 6 and dx >= min_h_len:
                my = (y1 + y2) / 2.0
                if by - 10 <= my <= by + bh + 10:
                    h_ys.append(my)

    x_axes = _cluster_coords(v_xs, max(18.0, bw * 0.06))[:14]
    y_axes = _cluster_coords(h_ys, max(18.0, bh * 0.06))[:12]
    if len(x_axes) < 2:
        x_axes = [float(bx), float(bx + bw)]
    if len(y_axes) < 2:
        y_axes = [float(by), float(by + bh)]
    return x_axes, y_axes


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

    spans_x, spans_y = max(1, len(x_axes) - 1), max(1, len(y_axes) - 1)
    step_m = max(1.0, axis_step_mm / 1000.0)
    est_length_m, est_width_m = round(spans_x * step_m, 1), round(spans_y * step_m, 1)
    est_area_m2 = round(est_length_m * est_width_m * (extent_pct / 100.0), 1)

    svg_w, svg_h = 460, 300
    pad_l, pad_r, pad_t, pad_b = 46, 26, 32, 46
    draw_w, draw_h = svg_w - pad_l - pad_r, svg_h - pad_t - pad_b
    scale = min(draw_w / max(1, bw), draw_h / max(1, bh))
    offset_x = pad_l + (draw_w - bw * scale) / 2.0
    offset_y = pad_t + (draw_h - bh * scale) / 2.0

    poly_str = " ".join(f"{round(offset_x + (pt - bx) * scale, 1)},{round(offset_y + (pt - by) * scale, 1)}" for pt in approx)
    axes_svg = []
    for idx, ax_x in enumerate(x_axes, start=1):
        sx = round(offset_x + (ax_x - bx) * scale, 1)
        axes_svg.append(
            f'<line x1="{sx}" y1="{pad_t - 10}" x2="{sx}" y2="{svg_h - 28}" stroke="#f59e0b" stroke-width="1" stroke-dasharray="7 3 2 3" opacity="0.85"/>'
            f'<circle cx="{sx}" cy="{svg_h - 16}" r="10" fill="#0f172a" stroke="#f59e0b" stroke-width="1.4"/>'
            f'<text x="{sx}" y="{svg_h - 12}" fill="#fbbf24" font-size="10" font-weight="bold" text-anchor="middle" font-family="sans-serif">{idx}</text>'
        )
    for idx, ay_y in enumerate(reversed(y_axes)):
        sy = round(offset_y + (ay_y - by) * scale, 1)
        letter = RU_AXIS_LETTERS[idx] if idx < len(RU_AXIS_LETTERS) else f"О{idx + 1}"
        axes_svg.append(
            f'<line x1="28" y1="{sy}" x2="{svg_w - 14}" y2="{sy}" stroke="#38bdf8" stroke-width="1" stroke-dasharray="7 3 2 3" opacity="0.85"/>'
            f'<circle cx="16" cy="{sy}" r="10" fill="#0f172a" stroke="#38bdf8" stroke-width="1.4"/>'
            f'<text x="16" y="{sy + 4}" fill="#38bdf8" font-size="10" font-weight="bold" text-anchor="middle" font-family="sans-serif">{letter}</text>'
        )

    svg_code = (
        f'<svg viewBox="0 0 {svg_w} {svg_h}" width="100%" height="260" style="background:#090d16;border:1px solid #1e293b;border-radius:10px;">'
        + "".join(axes_svg)
        + f'<polygon points="{poly_str}" fill="rgba(56,189,248,0.18)" stroke="#e2e8f0" stroke-width="2.5"/>'
        + f'<text x="{pad_l}" y="16" fill="#94a3b8" font-size="11" font-family="monospace">Черепаха CAD-Оси · Осей X:{len(x_axes)} Y:{len(y_axes)} · ~{est_length_m}×{est_width_m}м</text></svg>'
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
    r'((?:боковое|верхнее|нижнее)?\s*(?:сопряжение|примыкание|узел|разрез|сечение|схема|крепление|пожарная\s+отсечка)[^\n]{3,95})',
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
