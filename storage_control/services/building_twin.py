import re
from storage_control.models import ParsedPage, PurchaseRequest, PhotoIntake


def fix_autocad_mojibake(text: str) -> str:
    if not text:
        return ""
    if any(ch in text for ch in ("\u00dd", "\u00cf", "\u00ee", "\u00e5", "\u00f9", "\u00e6", "\u00c0", "\u00c1", "\u00c2")):
        try:
            repaired = text.encode("latin1").decode("cp1251")
            if any("\u0410" <= c <= "\u044f" or c in "\u0401\u0451" for c in repaired):
                return repaired
        except Exception:
            pass
    return text


RE_ROOM = re.compile(
    r'(?:^|\s)(\d{3}(?:\.\d{1,2})?)\s+([\u0410-\u042f\u0401][\u0410-\u042f\u0401\u0430-\u044f\u04510-9\s\-\(\)\.,]{3,48}?)\s+(\d{1,4}[\.,]\d{2})(?=\s|$)'
)

GARBAGE_WORDS = (
    "\u043b\u0438\u0441\u0442", "\u043c\u0430\u0441\u0448\u0442\u0430\u0431", "\u0433\u043e\u0441\u0442",
    "\u0434\u0430\u0442\u0430", "\u043f\u043e\u0434\u043f", "\u0438\u043d\u0432",
    "\u0438\u0442\u043e\u0433\u043e", "\u0432\u0441\u0435\u0433\u043e",
    "\u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442", "\u043f\u0440\u043e\u0432\u0435\u0440",
    "\u0433\u0438\u043f", "\u043d.\u043a\u043e\u043d\u0442\u0440", "\u0443\u0442\u0432",
    "\u0431\u0430\u043b\u0430\u043d\u043e\u0432\u0441\u043a", "\u043f\u043b\u0430\u0442\u043e\u043d\u043e\u0432",
    "\u043c\u0430\u043b\u044f\u043a\u0438\u043d", "\u0432\u043b\u0430\u0434\u0438\u0441\u043b\u0430\u0432",
    "\u0442\u0438\u043f ", "\u043f\u043b\u0438\u0442\u0430", "\u043a\u0438\u0440\u043f\u0438\u0447",
    "\u0431\u0435\u0442\u043e\u043d", "\u043e\u043a \u0441\u0437", "\u043e\u043a \u0441\u0432",
    "\u043e\u043a \u044e\u0437", "\u043e\u043a \u044e\u0432",
)


FLOOR_ELEVATIONS = {
    0: ("\u041f\u043e\u0434\u0432\u0430\u043b (0xx)", "\u043e\u0442\u043c. -3,640 \u043c"),
    1: ("1-\u0439 \u044d\u0442\u0430\u0436 (1xx)", "\u043e\u0442\u043c. 0,000 \u043c"),
    2: ("2-\u0439 \u044d\u0442\u0430\u0436 (2xx)", "\u043e\u0442\u043c. +4,200 \u043c"),
    3: ("3-\u0439 \u044d\u0442\u0430\u0436 (3xx)", "\u043e\u0442\u043c. +8,400 \u043c"),
    4: ("4-\u0439 \u044d\u0442\u0430\u0436 (4xx)", "\u043e\u0442\u043c. +12,600 \u043c"),
    5: ("5-\u0439 \u044d\u0442\u0430\u0436 (5xx)", "\u043e\u0442\u043c. +16,800 \u043c"),
}

def _floor_for_code(code: str) -> tuple[int, str]:
    c0 = (code or "1")
    n = int(c0) if c0.isdigit() else 1
    lbl, elev = FLOOR_ELEVATIONS.get(n, (f"{n}-\u0439 \u044d\u0442\u0430\u0436", ""))
    return n, f"{lbl} \u00b7 {elev}".strip(" \u00b7")

SPECIAL_NODES_CATALOG = [
    {"icon": "\U0001f6d7", "title": "\u041b\u0438\u0444\u0442\u044b \u0438 \u043b\u0438\u0444\u0442\u043e\u0432\u044b\u0435 \u0448\u0430\u0445\u0442\u044b", "elev": "\u043e\u0442\u043c. -3,640 \u2192 +16,800 \u043c", "aosr": "\u0410\u041e\u0421\u0420 \u043d\u0430 \u043f\u0440\u0438\u044f\u043c\u043e\u043a \u043b\u0438\u0444\u0442\u0430, \u0433\u0438\u0434\u0440\u043e\u0438\u0437\u043e\u043b\u044f\u0446\u0438\u044e \u0438 \u0437\u0430\u043a\u043b\u0430\u0434\u043d\u044b\u0435 \u0448\u0430\u0445\u0442\u044b"},
    {"icon": "\U0001f573\ufe0f", "title": "\u041f\u0440\u0438\u044f\u043c\u043a\u0438 \u0438 \u0434\u0440\u0435\u043d\u0430\u0436\u043d\u044b\u0435 \u0441\u0438\u0441\u0442\u0435\u043c\u044b", "elev": "\u043e\u0442\u043c. -3,640 \u043c (\u043f\u043e\u0434\u0432\u0430\u043b / \u0418\u0422\u041f / \u043d\u0430\u0441\u043e\u0441\u043d\u0430\u044f)", "aosr": "\u0410\u041e\u0421\u0420 \u043d\u0430 \u0433\u0438\u0434\u0440\u043e\u0438\u0437\u043e\u043b\u044f\u0446\u0438\u044e \u043f\u0440\u0438\u044f\u043c\u043a\u043e\u0432 \u0438 \u043f\u0440\u0438\u0441\u0442\u0435\u043d\u043d\u044b\u0439 \u0434\u0440\u0435\u043d\u0430\u0436"},
    {"icon": "\U0001f4a7", "title": "\u041a\u043e\u043b\u043e\u0434\u0446\u044b \u043d\u0430\u0440\u0443\u0436\u043d\u044b\u0445 \u0441\u0435\u0442\u0435\u0439 (\u041a\u041a\u0421 / \u0412\u041a / \u041d\u0412\u041a)", "elev": "\u043e\u0442\u043c. -1,100 \u2192 -0,950 \u043c (\u0432\u0432\u043e\u0434 \u0432 \u041f\u043e\u043c. 017)", "aosr": "\u0410\u041e\u0421\u0420 \u043d\u0430 \u043e\u0441\u043d\u043e\u0432\u0430\u043d\u0438\u0435, \u0433\u0438\u0434\u0440\u043e\u0438\u0437\u043e\u043b\u044f\u0446\u0438\u044e \u043a\u043e\u043b\u043e\u0434\u0446\u0435\u0432 \u0438 \u043e\u0431\u0440\u0430\u0442\u043d\u0443\u044e \u0437\u0430\u0441\u044b\u043f\u043a\u0443"},
    {"icon": "\u26a1", "title": "\u041c\u043e\u043b\u043d\u0438\u0435\u043e\u0442\u0432\u043e\u0434 \u0438 \u043a\u043e\u043d\u0442\u0443\u0440 \u0437\u0430\u0437\u0435\u043c\u043b\u0435\u043d\u0438\u044f", "elev": "\u041a\u0440\u043e\u0432\u043b\u044f (+16,800 \u043c) \u2192 \u0413\u0440\u0443\u043d\u0442 (-3,640 \u043c)", "aosr": "\u0410\u041e\u0421\u0420 \u043d\u0430 \u0441\u043a\u0440\u044b\u0442\u044b\u0439 \u043c\u043e\u043d\u0442\u0430\u0436 \u0442\u043e\u043a\u043e\u043e\u0442\u0432\u043e\u0434\u043e\u0432 \u0438 \u0437\u0430\u0437\u0435\u043c\u043b\u0438\u0442\u0435\u043b\u0435\u0439 + \u043f\u0440\u043e\u0442\u043e\u043a\u043e\u043b \u042d\u0422\u041b"},
    {"icon": "\U0001fa9c", "title": "\u041b\u0435\u0441\u0442\u043d\u0438\u0447\u043d\u044b\u0435 \u043a\u043b\u0435\u0442\u043a\u0438 \u0438 \u044d\u0432\u0430\u043a\u0443\u0430\u0446\u0438\u044f", "elev": "\u043e\u0442\u043c. -3,640 \u2192 +16,800 \u043c", "aosr": "\u0410\u041e\u0421\u0420 \u043d\u0430 \u043c\u043e\u043d\u0442\u0430\u0436 \u043b\u0435\u0441\u0442\u043d\u0438\u0447\u043d\u044b\u0445 \u043c\u0430\u0440\u0448\u0435\u0439, \u043e\u0433\u0440\u0430\u0436\u0434\u0435\u043d\u0438\u0439 \u0438 \u0434\u044b\u043c\u043e\u0443\u0434\u0430\u043b\u0435\u043d\u0438\u044f"},
]


def infer_room_work_layers(room_name: str) -> dict:
    low = (room_name or "").lower()
    if any(k in low for k in ("\u0432\u0432\u043e\u0434\u0430 \u043a\u0430\u0431\u0435\u043b", "\u0438\u0431\u043f", "\u044d\u043b\u0435\u043a\u0442\u0440\u043e\u0449\u0438\u0442")):
        return {
            "walls": "\u0428\u0442\u0443\u043a\u0430\u0442\u0443\u0440\u043a\u0430 + \u043e\u0433\u043d\u0435\u0437\u0430\u0449\u0438\u0442\u043d\u0430\u044f \u043e\u043a\u0440\u0430\u0441\u043a\u0430 (EI-60)",
            "floors": "\u0410\u043d\u0442\u0438\u0441\u0442\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u0438\u0439 \u043d\u0430\u043b\u0438\u0432\u043d\u043e\u0439 \u043f\u043e\u043b + \u043a\u043e\u043d\u0442\u0443\u0440 \u0437\u0430\u0437\u0435\u043c\u043b\u0435\u043d\u0438\u044f",
            "sleeves": "\u0412\u0432\u043e\u0434\u043d\u044b\u0435 \u0433\u0438\u043b\u044c\u0437\u044b \u00d8110/160 \u0441 \u0433\u0435\u0440\u043c\u0435\u0442\u0438\u0437\u0430\u0446\u0438\u0435\u0439 + \u043c\u0443\u0444\u0442\u044b \u0424\u0417-123",
            "mep": "\u041b\u043e\u0442\u043a\u0438 \u0421\u041a\u041a, \u043a\u0440\u043e\u0441\u0441\u044b \u0421\u041a\u0421, \u0449\u0438\u0442\u044b \u042d\u0421, \u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u043a\u0430 \u0410\u0423\u041f\u0422",
        }
    return {
        "walls": "\u041f\u0435\u0440\u0435\u0433\u043e\u0440\u043e\u0434\u043a\u0438, \u0448\u043f\u0430\u043a\u043b\u0451\u0432\u043a\u0430, \u0447\u0438\u0441\u0442\u043e\u0432\u0430\u044f \u043e\u043a\u0440\u0430\u0441\u043a\u0430 / \u043e\u0442\u0434\u0435\u043b\u043a\u0430",
        "floors": "\u0421\u0442\u044f\u0436\u043a\u0430 \u043f\u043e\u043b\u0430 + \u043a\u0435\u0440\u0430\u043c\u043e\u0433\u0440\u0430\u043d\u0438\u0442 / \u043b\u0438\u043d\u043e\u043b\u0435\u0443\u043c",
        "sleeves": "\u0413\u0438\u043b\u044c\u0437\u044b \u0432 \u043f\u0435\u0440\u0435\u0433\u043e\u0440\u043e\u0434\u043a\u0430\u0445 \u043f\u043e\u0434 \u0441\u043b\u0430\u0431\u043e\u0442\u043e\u0447\u043a\u0443 \u0421\u041a\u0421 \u0438 \u044d\u043b\u0435\u043a\u0442\u0440\u0438\u043a\u0443 \u042d\u0421",
        "mep": "\u0417\u0430\u043f\u043e\u0442\u043e\u043b\u043e\u0447\u043d\u044b\u0435 \u043b\u043e\u0442\u043a\u0438 \u0421\u041a\u041a, \u0441\u0432\u0435\u0442\u0438\u043b\u044c\u043d\u0438\u043a\u0438 \u042d\u041e, \u0440\u0435\u0448\u0451\u0442\u043a\u0438 \u041e\u0412, \u0440\u043e\u0437\u0435\u0442\u043a\u0438 \u0421\u041a\u0421",
    }


def build_building_twin_index() -> dict:
    rooms_by_code = {}
    pages = ParsedPage.objects.select_related("document").order_by("document_id", "page_number")[:300]
    photos = list(PhotoIntake.objects.all().values("id", "notes", "ocr_raw_text", "detected_axes"))

    for pg in pages:
        clean_txt = fix_autocad_mojibake(pg.text or "")
        for m in RE_ROOM.finditer(clean_txt):
            code = m.group(1).strip()
            name = re.sub(r'\s+', ' ', m.group(2)).strip(" -.,:")
            area = float(m.group(3).replace(",", "."))
            low_n = name.lower()
            if len(name) < 4 or area <= 1.0 or area > 4000 or any(bad in low_n for bad in GARBAGE_WORDS):
                continue
            floor_num, floor_label = _floor_for_code(code)
            matched_ph = [p for p in photos if code in (p.get("notes") or "") or code in (p.get("ocr_raw_text") or "") or code in (p.get("detected_axes") or "")]
            pct = min(100, len(matched_ph) * 25)
            entry = rooms_by_code.setdefault(code, {
                "code": code, "name": name, "area_m2": area,
                "floor_num": floor_num, "floor_label": floor_label,
                "progress_pct": pct, "photos_count": len(matched_ph),
                "layers": infer_room_work_layers(name), "pages": [],
            })
            if len(name) > len(entry["name"]):
                entry["name"] = name
                entry["layers"] = infer_room_work_layers(name)

    floors_map = {}
    for rm in sorted(rooms_by_code.values(), key=lambda x: (x["floor_num"], x["code"])):
        fl = floors_map.setdefault(rm["floor_label"], {"floor_num": rm["floor_num"], "floor_label": rm["floor_label"], "rooms": [], "total_area": 0.0, "progress_pct": 0})
        fl["rooms"].append(rm)
        fl["total_area"] = round(fl["total_area"] + rm["area_m2"], 2)
    for fl in floors_map.values():
        if fl["rooms"]:
            fl["progress_pct"] = round(sum(r["progress_pct"] for r in fl["rooms"]) / len(fl["rooms"]))
    return {"total_rooms": len(rooms_by_code), "floors": list(floors_map.values()), "rooms_map": rooms_by_code, "special_nodes": SPECIAL_NODES_CATALOG}


def build_single_room_passport(room_code: str) -> dict:
    twin = build_building_twin_index()
    rc = (room_code or "").strip()
    fl_num, fl_lbl = _floor_for_code(rc)
    room_info = twin["rooms_map"].get(rc) or {
        "code": rc, "name": f"\u041f\u043e\u043c\u0435\u0449\u0435\u043d\u0438\u0435 {rc}", "area_m2": 0.0,
        "floor_num": fl_num, "floor_label": fl_lbl, "progress_pct": 0, "photos_count": 0,
        "layers": infer_room_work_layers(""), "pages": [],
    }
    all_pages = []
    for pg in ParsedPage.objects.select_related("document").filter(text__contains=rc).order_by("document__title", "page_number")[:30]:
        txt = fix_autocad_mojibake(pg.text or "")
        idx = txt.find(rc)
        snippet = re.sub(r'\s+', ' ', txt[max(0, idx - 60): idx + 140]).strip() if idx >= 0 else ""
        all_pages.append({"doc_id": pg.document_id, "doc_title": pg.document.title if pg.document else "", "page_number": pg.page_number, "snippet": snippet})
    related_reqs = list(PurchaseRequest.objects.filter(room_info__icontains=rc).values("id", "discipline", "material_name", "required_qty", "unit", "status")[:25])
    return {"room": room_info, "pages": all_pages, "requests": related_reqs}
