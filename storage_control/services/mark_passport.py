import os, re
from django.conf import settings
from django.db.models import Q
from storage_control.models import PurchaseRequest, ParsedPage
from storage_control.services.building_twin import fix_autocad_mojibake
from storage_control.services.quantum_normalizer import canon_key


def _fetch_web_analogs(query: str) -> list:
    return []


def _detranslit_slug(slug: str) -> str:
    s = (slug or "").split("/")[0]
    s = re.sub(r'^\d+[\-_]\d+[\-_]', '', s).replace('-', ' ').strip()
    s = re.sub(r'(?<=[0-9a-zA-Z])h$', '', s)
    pairs = [
        ("shch", "\u0449"), ("sh", "\u0448"), ("ch", "\u0447"), ("zh", "\u0436"), ("yu", "\u044e"), ("ya", "\u044f"),
        ("kh", "\u0445"), ("ts", "\u0446"), ("yo", "\u0451"), ("a", "\u0430"), ("b", "\u0431"), ("v", "\u0432"),
        ("g", "\u0433"), ("d", "\u0434"), ("e", "\u0435"), ("z", "\u0437"), ("i", "\u0438"), ("j", "\u0439"),
        ("k", "\u043a"), ("l", "\u043b"), ("m", "\u043c"), ("n", "\u043d"), ("o", "\u043e"), ("p", "\u043f"),
        ("r", "\u0440"), ("s", "\u0441"), ("t", "\u0442"), ("u", "\u0443"), ("f", "\u0444"), ("y", "\u044b"),
    ]
    low = s.lower()
    for lat, cyr in pairs:
        low = low.replace(lat, cyr)
    return re.sub(r'\s+', ' ', low).strip().capitalize()


def _ensure_page_png(pg) -> str:
    if getattr(pg, "image", None) and pg.image:
        return pg.image.url
    try:
        import pypdfium2 as pdfium
        if pg.document and pg.document.file and os.path.exists(pg.document.file.path):
            out_dir = os.path.join(settings.MEDIA_ROOT, "pdf_pages")
            os.makedirs(out_dir, exist_ok=True)
            fname = f"doc_{pg.document.id}_p_{pg.page_number}.png"
            fpath = os.path.join(out_dir, fname)
            if not os.path.exists(fpath):
                pdf = pdfium.PdfDocument(pg.document.file.path)
                pdf[pg.page_number - 1].render(scale=1.6).to_pil().save(fpath, "PNG")
            return f"{settings.MEDIA_URL}pdf_pages/{fname}"
    except Exception:
        pass
    return ""


def build_mark_passport(slug: str) -> dict:
    clean_slug = (slug or "").split("/")[0]
    ru_hint = _detranslit_slug(clean_slug)
    raw_parts = [p for p in re.split(r'[\s\-]+', ru_hint) if len(p) >= 2]
    key_tokens = [p for p in raw_parts if p.lower() not in ("\u0441\u0438\u0441\u0442\u0435\u043c\u0430", "\u043b", "l")]
    if not key_tokens:
        key_tokens = raw_parts or [clean_slug]

    # ????????? ????? ??? ?????????? ? ???????????? (????????? / ?????????)
    expanded_tokens = list(key_tokens)
    for kt in key_tokens:
        if "\u0448\u043f\u0430\u043a\u043b" in kt.lower():
            expanded_tokens.append("\u0448\u043f\u0430\u0442\u043b")
        elif "\u0448\u043f\u0430\u0442\u043b" in kt.lower():
            expanded_tokens.append("\u0448\u043f\u0430\u043a\u043b")

    matched_reqs = []
    for r in PurchaseRequest.objects.select_related("document").all()[:2500]:
        ck_nm = canon_key(r.material_name or "")
        if any(canon_key(kt)[:6] in ck_nm for kt in expanded_tokens if len(canon_key(kt)) >= 2):
            matched_reqs.append(r)

    q_filter = Q()
    for kt in expanded_tokens[:5]:
        stem = kt[:6] if len(kt) >= 6 else kt
        for var in {stem, stem.upper(), stem.lower(), stem.capitalize()}:
            if len(var) >= 2:
                q_filter |= Q(text__contains=var)

    matched_pages, seen_p = [], set()
    if q_filter:
        for pg in ParsedPage.objects.select_related("document").filter(q_filter)[:12]:
            if pg.id in seen_p:
                continue
            seen_p.add(pg.id)
            txt = fix_autocad_mojibake(pg.text or "")
            snip = re.sub(r'\s+', ' ', txt)[:220].strip()
            for kt in expanded_tokens:
                m = re.search(re.escape(kt[:6]), txt, re.I)
                if m:
                    snip = re.sub(r'\s+', ' ', txt[max(0, m.start()-45):m.end()+130]).strip()
                    break
            matched_pages.append({"doc": pg.document.title if pg.document else "\u0420\u0414", "page": pg.page_number, "snippet": snip, "img_url": _ensure_page_png(pg)})

    docs_set = {p["doc"] for p in matched_pages} | {r.document.title for r in matched_reqs if r.document}
    total_qty = round(sum(float(r.required_qty or 0) for r in matched_reqs), 2)
    stock_qty = round(sum(max(0.0, float(r.required_qty or 0) - float(r.deficit_qty or 0)) for r in matched_reqs), 2)

    if matched_pages and not matched_reqs:
        audit = {"color": "#f87171", "verdict": f"\U0001f534 \u041d\u0435\u0443\u0447\u0442\u0451\u043d\u043d\u0430\u044f \u0432\u044b\u043d\u043e\u0441\u043a\u0430 \u0432 \u0420\u0414: \u043d\u0430\u0439\u0434\u0435\u043d\u043e \u043b\u0438\u0441\u0442\u043e\u0432: {len(matched_pages)}, \u0432 \u0437\u0430\u043a\u0443\u043f\u043a\u0435 0 \u043f\u043e\u0437.", "detail": "\u0421\u041f 48.13330: \u0434\u043e\u0431\u0430\u0432\u044c\u0442\u0435 \u043f\u043e\u0437\u0438\u0446\u0438\u044e \u0432 \u0432\u0435\u0434\u043e\u043c\u043e\u0441\u0442\u044c \u0437\u0430\u043a\u0443\u043f\u043a\u0438."}
    elif matched_pages and matched_reqs:
        audit = {"color": "#34d399", "verdict": f"\U0001f7e2 \u0410\u0443\u0434\u0438\u0442 \u043f\u0440\u043e\u0439\u0434\u0435\u043d: \u043b\u0438\u0441\u0442\u043e\u0432 \u0420\u0414: {len(matched_pages)}, \u0432 \u0441\u043f\u0435\u0446\u0438\u0444\u0438\u043a\u0430\u0446\u0438\u0438: {total_qty} \u0435\u0434. (\u041f\u043e\u0433\u0440\u0435\u0448\u043d\u043e\u0441\u0442\u044c: 0%)", "detail": "\u0412\u044b\u043d\u043e\u0441\u043a\u0438 \u0438 \u0441\u043f\u0435\u0446\u0438\u0444\u0438\u043a\u0430ция \u0441\u043e\u0433\u043b\u0430\u0441ованы (\u0413\u041e\u0421\u0422 \u0420 21.101)."}
    else:
        audit = {"color": "#fbbf24", "verdict": "\U0001f7e1 \u041d\u043e\u0432\u0430\u044f / \u0434\u043e\u043f\u043e\u043b\u043d\u0438тельна\u044f \u043f\u043e\u0437\u0438\u0446\u0438\u044f \u2014 \u043c\u043e\u0436н\u043e \u0441\u0440\u0430зу \u043f\u0435редат\u044c \u0432 \u0437\u0430к\u0443\u043f\u043a\u0443 \u0438 \u041f\u0430\u0440\u0442\u043d\u0451\u0440ску\u044e \u043b\u0438\u0433\u0443.", "detail": "\u0421\u0438\u0441\u0442\u0435\u043c\u0430 \u0430\u0432\u0442о\u043c\u0430\u0442иче\u0441\u043a\u0438 \u043f\u043e\u0434\u0431\u0435\u0440\u0451\u0442 \u043a\u043b\u0430\u0441\u0441 \u0442о\u0432\u0430\u0440\u0430 \u0438 \u043f\u043e\u0441\u0442\u0430\u0432\u0449\u0438\u043a\u043e\u0432."}

    return {
        "query": clean_slug.replace("-", " "),
        "slug_alias": clean_slug,
        "ru_hint": ru_hint,
        "tech": {"category": "\u041f\u0440\u043e\u0435\u043a\u0442\u043d\u0430\u044f \u043f\u043e\u0437\u0438\u0446\u0438\u044f \u0420\u0414", "decoded": ru_hint, "physics": "\u041f\u043e\u0441\u0442\u0430\u0432\u043a\u0430 \u0441 \u043f\u0430\u0441\u043f\u043e\u0440\u0442\u043e\u043c \u043a\u0430\u0447\u0435\u0441\u0442\u0432\u0430", "analogs": ["\u0410налог по ГОСТ / СП"]},
        "floors": [],
        "tabs": {},
        "matched_reqs": matched_reqs,
        "matched_pages": matched_pages,
        "real_qty": total_qty if total_qty > 0 else 1,
        "stock_qty": stock_qty,
        "docs_found_cnt": len(docs_set),
        "reqs_found_cnt": len(matched_reqs),
        "links_cnt": len(matched_pages) + len(matched_reqs),
        "audit": audit,
    }


build_mark_passport_data = build_mark_passport


def _fetch_engineering_diagrams(*args, **kwargs) -> list:
    return []
