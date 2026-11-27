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
    is_formula = ("√" in low) or ("=" in low and any(op in low for op in ("/", "*", "·", "3600", "11000")))
    if is_formula or any(p in low for p in rules["design_note_patterns"]):
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


from storage_control.services.quantum_normalizer import canon_key as canonicalize_spec_text

def build_work_sequence_cascade(name: str) -> str:
    """?????????? ??????????????? ?????????????????? ????? ??? ? ???????? ??? ??? ???????."""
    c = canonicalize_spec_text(name)
    if "\u0432\u043e\u0437\u0434\u0443\u0445\u043e\u0432\u043e\u0434" in c:
        return "1. \u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0423\u041f\u0414 \u2192 2. \u0420\u0430\u0437\u043c\u0435\u0442\u043a\u0430 \u0438 \u0448\u043f\u0438\u043b\u044c\u043a\u0438 \u2192 3. \u041c\u043e\u043d\u0442\u0430\u0436 \u0432\u043e\u0437\u0434\u0443\u0445\u043e\u0432\u043e\u0434\u043e\u0432 \u0438 \u043f\u0440\u043e\u0445\u043e\u0434\u043e\u043a EI 90 \u2192 4. \u041f\u0443\u0441\u043a\u043e\u043d\u0430\u043b\u0430\u0434\u043a\u0430 \u0438 \u0410\u041e\u0421\u0420"
    if any(k in c for k in ("\u0444\u043b\u0430\u043d\u0435\u0446", "\u043a\u0440\u0430\u043d", "\u0442\u0440\u0443\u0431")):
        return "1. \u0412\u0445\u043e\u0434\u043d\u043e\u0439 \u043a\u043e\u043d\u0442\u0440\u043e\u043b\u044c \u0414\u0443/\u0420\u0443 \u2192 2. \u041c\u043e\u043d\u0442\u0430\u0436 \u0443\u0437\u043b\u0430 \u0438 \u043f\u0440\u043e\u043a\u043b\u0430\u0434\u043e\u043a \u2192 3. \u041e\u043f\u0440\u0435\u0441\u0441\u043e\u0432\u043a\u0430 \u2192 4. \u0410\u041e\u0421\u0420 \u2116 344/\u043f\u0440"
    if any(k in c for k in ("\u0440\u0430\u043c\u0430", "\u0430\u0440\u043c\u0430\u0442", "\u043f\u0440\u043e\u0444\u0438\u043b", "\u0431\u043e\u043b\u0442")):
        return "1. \u0421\u043a\u043b\u0430\u0434 (\u0423\u041f\u0414 + \u0441\u0435\u0440\u0442\u0438\u0444\u0438\u043a\u0430\u0442 \u043c\u0435\u0442\u0430\u043b\u043b\u0430) \u2192 2. \u0413\u0435\u043e\u0434\u0435\u0437\u0438\u044f \u043e\u0441\u0435\u0439 \u2192 3. \u0421\u0431\u043e\u0440\u043a\u0430 \u0438 \u0430\u043d\u0442\u0438\u043a\u043e\u0440 \u2192 4. \u0410\u041e\u0421\u0420"
    return "1. \u041f\u0440\u0438\u0451\u043c\u043a\u0430 \u0423\u041f\u0414 \u2192 2. \u0412\u044b\u0434\u0430\u0447\u0430 \u0432 \u043f\u0440\u043e\u0438\u0437\u0432\u043e\u0434\u0441\u0442\u0432\u043e (\u041c-11) \u2192 3. \u041c\u043e\u043d\u0442\u0430\u0436 \u043f\u043e \u0413\u041f\u0420 \u2192 4. \u0410\u041e\u0421\u0420 \u2116 344/\u043f\u0440"


def parse_grouped_gost_spec(text: str, page_num: int) -> list[dict]:
    """
    ?????? ??????? ???????????? ???? ? ?????????? ???????????:
    ?????????? '?????????? ?? ????????????? ???????????? ?????, ?=0.7 ??'
    ? ????????? ??? ? ?????? ???????? ??????? ??????? ('200?300 | ?.?. | 5,7 | ????? 20%').
    """
    active_group = ""
    active_gost = ""
    results = []
    group_triggers = (
        "\u0432\u043e\u0437\u0434\u0443\u0445\u043e\u0432\u043e\u0434",
        "\u043e\u0442\u0432\u043e\u0434",
        "\u043f\u0435\u0440\u0435\u0445\u043e\u0434",
        "\u0442\u0440\u043e\u0439\u043d\u0438\u043a",
        "\u043a\u043b\u0430\u043f\u0430\u043d",
        "\u0448\u0443\u043c\u043e\u0433\u043b\u0443\u0448",
    )
    for raw_ln in (text or "").splitlines():
        ln = re.sub(r'\s+', ' ', raw_ln).strip()
        low = ln.lower()
        if not ln:
            continue
        m_g = re.search(r'(?:\u0413\u041e\u0421\u0422|\u0421\u041f)\s*[0-9\-\.]+', ln)
        if m_g:
            active_gost = m_g.group(0)
        # ???? ?????? ? ????????? ?????? (??? ?????????? ? ?????)
        if any(gt in low for gt in group_triggers) and not re.search(r'(?:\u043f\.\u043c\.?|\u0448\u0442\.?)\s+\d', low):
            active_group = re.sub(r'(?:\u0413\u041e\u0421\u0422|\u0421\u041f)\s*[0-9\-\.]+', '', ln).strip(" ,.-")
            continue
        # ???????? ?????? ???????/???????? + ??????? + ?????????? (????????: "200?300 ?.?. 5,7 ????? 20%")
        m_child = re.match(r'^((?:\d{2,4}[xX\u0445\u00d7]\d{2,4}|(?:\u00d8|\u2300|d)\s*\d{2,4})[^\n]{0,35}?)\s+(\u043f\.\u043c\.?|\u0448\u0442\.?|\u043c2|\u043c\u00b2|\u043c)\s+(\d+(?:[\.,]\d+)?)', ln, re.I)
        if m_child and active_group:
            sec = m_child.group(1).strip()
            unit_raw = m_child.group(2).strip()
            base_qty = float(m_child.group(3).replace(",", "."))
            has_20 = "20%" in low or "\u0437\u0430\u043f\u0430\u0441" in low
            final_qty = round(base_qty * 1.2, 2) if has_20 else base_qty
            justif = f"\u0422\u0440\u0430\u0441\u0441\u0430 {base_qty} + 20% \u0437\u0430\u043f\u0430\u0441 \u0421\u041f = {final_qty}" if has_20 else f"\u041f\u043e \u0441\u043f\u0435\u0446\u0438\u0444\u0438\u043a\u0430\u0446\u0438\u0438 \u0420\u0414 ({base_qty})"
            full_name = f"{active_group} {sec}" + (f" ({active_gost})" if active_gost else "")
            results.append({
                "name": full_name[:145],
                "unit": "\u043c" if "\u043f.\u043c" in unit_raw.lower() else unit_raw,
                "base_qty": base_qty,
                "qty": final_qty,
                "justification": justif,
                "page": page_num,
            })
    return results
