import re

HOMOGLYPHS = str.maketrans({
    "a": "\u0430", "b": "\u0432", "c": "\u0441", "e": "\u0435", "h": "\u043d",
    "k": "\u043a", "m": "\u043c", "o": "\u043e", "p": "\u0440", "t": "\u0442",
    "x": "\u0445", "y": "\u0443",
})


def canon_key(text: str) -> str:
    s = (text or "").strip().lower()
    s = s.replace("\u00d7", "\u0445").replace("*", "\u0445")
    s = re.sub(r'[\u2012\u2013\u2014\u2015\-]+', ' ', s)
    s = re.sub(r'(\d)\.(\d)', lambda m: m.group(1) + ',' + m.group(2), s)
    s = s.translate(HOMOGLYPHS)
    s = re.sub(r'(\d)\s*\u0445\s*(\d)', lambda m: m.group(1) + '\u0445' + m.group(2), s)
    s = re.sub(r'(?:\u0434\u0443|dn)\s*(\d{2,4})', lambda m: '\u0434\u0443' + m.group(1), s)
    s = re.sub(r'[,;:\(\)\[\]]+', ' ', s)
    s = re.sub(r'\s+\u0438\s+', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def canon_record(name: str, raw_unit: str, qty: float = 0.0) -> dict:
    clean_nm = re.sub(r'(?:\b\d{2}\.\d{2}\b\s*){2,}', ' ', (name or "").strip())
    clean_nm = re.sub(r'(?:\b\d\b\s*){4,}', ' ', clean_nm)
    clean_nm = re.sub(r'\s+', ' ', clean_nm).strip()
    clean_nm = re.sub(r'(?:\u0414\u0443|DN)\s*(\d{2,4})', lambda m: "\u0414\u0443 " + m.group(1), clean_nm, flags=re.I)

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

    return {"name": clean_nm, "unit": unit, "qty": round(float(qty or 0.0), 3), "canon_key": canon_key(clean_nm), "needs_du": needs_du}


def match_canon_tokens(query: str, target_text: str) -> bool:
    q_tokens = [t for t in canon_key(query).split() if len(t) >= 2]
    if not q_tokens:
        return False
    t_canon = canon_key(target_text)
    return all(tk in t_canon for tk in q_tokens)


def run_full_db_canonical_sweep() -> int:
    from storage_control.models import PurchaseRequest
    updated = 0
    for pr in PurchaseRequest.objects.all():
        rec = canon_record(pr.material_name, pr.unit, pr.required_qty)
        if pr.material_name != rec["name"] or pr.unit != rec["unit"]:
            pr.material_name = rec["name"][:255]
            pr.unit = rec["unit"]
            pr.save(update_fields=["material_name", "unit"])
            updated += 1
    return updated
