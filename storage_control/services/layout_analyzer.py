# -*- coding: utf-8 -*-
import re

try:
    import fitz
    HAS_FITZ = True
except ImportError:
    HAS_FITZ = False

CODE_RE = re.compile(r'([0-9]{1,2}(?:\.\d{4})?-[А-ЯЁA-Z]{1,3}(?:-[А-ЯЁ0-9.]{1,10})?)')


def analyze_zones(page) -> dict:
    """Делит лист на 3 функциональные зоны: штамп (правый низ), правая таблица, центр-графика."""
    if HAS_FITZ and hasattr(page, "rect"):
        w, h = page.rect.width, page.rect.height
        stamp_rect = fitz.Rect(w * 0.55, h * 0.72, w, h)
        right_spec_rect = fitz.Rect(w * 0.52, 0, w, h * 0.72)
        center_graph_rect = fitz.Rect(0, 0, w * 0.52, h)

        stamp_txt = page.get_text("text", clip=stamp_rect).strip()
        spec_zone_txt = page.get_text("text", clip=right_spec_rect).strip()
    else:
        # Резервный разбор для pypdf (читаем нижнюю часть текста страницы, где находится штамп)
        full_txt = (page.extract_text() or "").strip() if hasattr(page, "extract_text") else str(page)
        stamp_txt = full_txt[-600:]
        spec_zone_txt = full_txt
        center_graph_rect = None

    m_code = CODE_RE.search(stamp_txt)
    stamp_code = m_code.group(1) if m_code else ""
    stage = "РД" if ("РД" in stamp_txt.upper() or "-Р-" in stamp_code) else "ПД"

    return {
        "stamp_code": stamp_code,
        "stage": stage,
        "has_right_spec": len(spec_zone_txt) > 30,
        "center_rect": center_graph_rect,
    }


