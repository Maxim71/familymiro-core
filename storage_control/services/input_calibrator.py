import os, re, json
from django.conf import settings

CAL_PATH = os.path.join(settings.BASE_DIR, "parser_calibration.json")

DEFAULT_CALIBRATION = {
    "version": "300Y-1.0",
    "noise_patterns": [
        "\u044d\u043a\u0441\u043f\u043b\u0438\u043a\u0430\u0446",
        "\u043d\u043e\u043c\u0435\u0440\u043f\u043e\u043c\u0435\u0449",
        "\u043d\u0430\u0438\u043c\u0435\u043d\u043e\u0432\u0430\u043d\u0438\u0435\u043f\u043b\u043e\u0449",
        "\u043e\u0431\u0449\u0438\u0435 \u0434\u0430\u043d\u043d\u044b\u0435",
        "\u043a1=", "\u043a2=", "k1=", "k2="
    ],
    "design_note_patterns": [
        "\u043e\u0431\u043b\u0430\u0434\u0430\u0435\u0442 \u043c\u0430\u0441\u0441\u043e\u0439",
        "\u043d\u0435 \u0434\u043e\u043b\u0436\u043d\u043e \u0431\u044b\u0442\u044c",
        "\u043c\u0435\u0436\u0434\u0443 \u0441\u0432\u044f\u0437",
        "\u043d\u0435 \u0434\u043e\u043f\u0443\u0441\u043a\u0430\u0435\u0442\u0441\u044f"
    ],
    "warranty_patterns": [
        "\u044d\u043a\u0441\u043f\u043b\u0443\u0430\u0442\u0430\u0446",
        "\u0433\u0430\u0440\u0430\u043d\u0442\u0438\u0439"
    ]
}


def load_calibration_rules() -> dict:
    if not os.path.exists(CAL_PATH):
        json.dump(DEFAULT_CALIBRATION, open(CAL_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return json.load(open(CAL_PATH, encoding="utf-8"))


def normalize_unit_and_name(name: str, raw_unit: str) -> tuple[str, str, bool]:
    """
    ???????????? ??? ? ??????? ????????? ?? ?????:
    - ?? 100 / DN100 / ??100 -> ?? 100
    - ?? / ??. -> ??., ? / ? -> ?
    - ?????????? (clean_name, clean_unit, requires_du_clarification)
    """
    clean_nm = re.sub(r'(?:\b\d{2}\.\d{2}\b\s*){2,}', ' ', (name or "").strip())
    clean_nm = re.sub(r'(?:\b\d\b\s*){4,}', ' ', clean_nm)
    clean_nm = re.sub(r'\s+', ' ', clean_nm).strip()
    clean_nm = re.sub(r'(?:\u0414\u0443|DN)\s*(\d{2,4})', lambda m: f"\u0414\u0443 {m.group(1)}", clean_nm, flags=re.I)

    low = clean_nm.lower()
    is_pipe_fitting = any(pk in low for pk in ("\u0444\u043b\u0430\u043d\u0435\u0446", "\u043a\u0440\u0430\u043d", "\u0437\u0430\u0434\u0432\u0438\u0436\u043a", "\u043a\u043b\u0430\u043f\u0430\u043d", "\u043e\u0442\u0432\u043e\u0434"))
    has_du = bool(re.search(r'(?:\u0414\u0443|DN|\u00d8)\s*\d{2,4}', clean_nm, re.I))
    needs_du = bool(is_pipe_fitting and not has_du)

    if "\u043b\u0435\u043d\u0442\u0430 \u0441\u0438\u0433\u043d\u0430\u043b" in low:
        unit = "\u043c"
    elif is_pipe_fitting:
        unit = "\u0448\u0442."
    elif any(k in low for k in ("\u0433\u0438\u0434\u0440\u043e\u0438\u0437\u043e\u043b", "\u0442\u0435\u0445\u043d\u043e\u044d\u043b\u0430\u0441\u0442", "\u043f\u043b\u0430\u043c\u044f \u0441\u0442\u043e\u043f")):
        unit = "\u043c\u00b2"
    elif any(k in low for k in ("\u0430500\u0441", "\u0430240", "34028", "\u0430\u0440\u043c\u0430\u0442")):
        unit = "\u043a\u0433"
    else:
        u = (raw_unit or "\u0448\u0442.").strip().lower().rstrip(".")
        unit = "\u0448\u0442." if u in ("\u0448\u0442", "pcs") else ("\u043c" if u in ("\u043c", "\u043f.\u043c") else (u or "\u0448\u0442."))

    return clean_nm, unit, needs_du


def classify_pdf_line_at_gate(raw_line: str) -> str:
    """
    ?????????????? ?????? ?? ????? ??? ???????? PDF:
    - STAMP_NOISE: ??????, ????? ???????????, ??????? ???????????? (?????????????)
    - DESIGN_NOTE: ????????? ?????????? ? ?????????? (? ?????????? ???, ?? ? ???????)
    - OPERATION_WARRANTY: ?????????? ? ???????????? ? ???????? (? ??????? ?????)
    - SPEC_ITEM: ?????? ??????? ???????????? ??? ???????
    """
    rules = load_calibration_rules()
    low = (raw_line or "").strip().lower()
    if len(low) < 8 or any(p in low for p in rules["noise_patterns"]):
        return "STAMP_NOISE"
    if any(p in low for p in rules["design_note_patterns"]):
        return "DESIGN_NOTE"
    if any(p in low for p in rules["warranty_patterns"]):
        return "OPERATION_WARRANTY"
    return "SPEC_ITEM"


def assign_words_to_gost_columns(words_xy: list[dict], page_width: float) -> list[dict]:
    """
    ?????????? ????? ?? ?????????? Y (?????? ??????? ?4.5 pt) ? ???????????? ?? X-???????? ????:
    pos (0..18%), name (18..56%), mark (56..73%), unit (73..81%), qty (81..89%), mass_note (89..100%).
    """
    if not words_xy or page_width <= 0:
        return []
    sorted_w = sorted(words_xy, key=lambda w: (-round(w["y"] / 4.5), w["x"]))
    rows, cur_row, cur_y = [], [], None
    for w in sorted_w:
        if cur_y is None or abs(w["y"] - cur_y) <= 4.5:
            cur_row.append(w)
            if cur_y is None:
                cur_y = w["y"]
        else:
            rows.append(sorted(cur_row, key=lambda item: item["x"]))
            cur_row, cur_y = [w], w["y"]
    if cur_row:
        rows.append(sorted(cur_row, key=lambda item: item["x"]))

    parsed_rows = []
    for r in rows:
        cols = {"pos": [], "name": [], "mark": [], "unit": [], "qty": [], "mass": []}
        for w in r:
            rx = w["x"] / page_width
            if rx < 0.18:
                cols["pos"].append(w["text"])
            elif rx < 0.56:
                cols["name"].append(w["text"])
            elif rx < 0.73:
                cols["mark"].append(w["text"])
            elif rx < 0.81:
                cols["unit"].append(w["text"])
            elif rx < 0.89:
                cols["qty"].append(w["text"])
            else:
                cols["mass"].append(w["text"])
        full_name = " ".join(cols["name"] + cols["mark"]).strip()
        if not full_name or classify_pdf_line_at_gate(full_name) != "SPEC_ITEM":
            continue
        raw_qty = " ".join(cols["qty"]).replace(",", ".")
        m_q = re.search(r'\d+(?:\.\d+)?', raw_qty)
        if not m_q:
            continue
        clean_nm, clean_u, needs_du = normalize_unit_and_name(full_name, " ".join(cols["unit"]))
        parsed_rows.append({
            "pos": " ".join(cols["pos"]).strip(),
            "name": clean_nm,
            "unit": clean_u,
            "qty": float(m_q.group(0)),
            "needs_du": needs_du,
            "mass_note": " ".join(cols["mass"]).strip(),
        })
    return parsed_rows


def extract_gost_table_rows_xy(pdf_path: str, page_index: int = 0) -> list[dict]:
    """????????? ?????? ???????????? ???? ?? ?????????? PDF ? ??????? X/Y ???????????? ????? pypdfium2."""
    try:
        import pypdfium2 as pdfium
        pdf = pdfium.PdfDocument(pdf_path)
        if page_index >= len(pdf):
            return []
        page = pdf[page_index]
        pw, _ = page.get_size()
        tp = page.get_textpage()
        n_chars = tp.count_chars()
        words_xy, cur_chars, wx, wy = [], [], 0.0, 0.0
        for i in range(n_chars):
            ch = tp.get_text_range(i, 1)
            l, b, r, top = tp.get_charbox(i)
            if ch.isspace():
                if cur_chars:
                    words_xy.append({"text": "".join(cur_chars), "x": wx, "y": wy})
                    cur_chars = []
            else:
                if not cur_chars:
                    wx, wy = l, top
                cur_chars.append(ch)
        if cur_chars:
            words_xy.append({"text": "".join(cur_chars), "x": wx, "y": wy})
        return assign_words_to_gost_columns(words_xy, pw)
    except Exception:
        return []
