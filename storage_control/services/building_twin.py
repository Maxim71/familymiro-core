import re
from storage_control.models import ParsedPage, PurchaseRequest


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


# ????? 1 ? 2: ???????????? ?????? (001, 501.2) ? ?????????? ??????? (?-101, ?-204) + ??????? ? 2 ???????
RE_MODE_1_2 = re.compile(
    r'(?:^|\s)((?:[\u0410-\u042fA-Z]\-)?\d{1,3}(?:\.\d{1,2})?)\s+([\u0410-\u042f\u0401][\u0410-\u042f\u0401\u0430-\u044f\u04510-9\s\-\(\)\.,]{3,55}?)\s+(\d{1,4}[\.,]\d{2})(?=\s|$)'
)
# ????? 3: ?????? ????? ?? ????? ("???. 035 ... 24,50 ?2" ??? "????????? 12 ... S=18.40")
RE_MODE_3 = re.compile(
    r'(?:\u043f\u043e\u043c\.?|\u043f\u043e\u043c\u0435\u0449\u0435\u043d\u0438\u0435)\s*(\d{1,3}(?:\.\d{1,2})?)[\s\-\u2014:]+([\u0410-\u042f\u0401\u0430-\u044f\u04510-9\s\-\(\)]{3,45}?)(?:S\s*=\s*)?(\d{1,4}[\.,]\d{1,2})\s*(?:\u043c2|\u043c\u00b2)',
    re.I,
)
# ????? 4: ???????? ??????????? ????????? ??? ?????? ???????? ?? / ?? / ?? / ??? ??
TECH_ROOMS_KEYWORDS = (
    "\u0432\u0435\u043d\u0442\u043a\u0430\u043c\u0435\u0440",
    "\u044d\u043b\u0435\u043a\u0442\u0440\u043e\u0449\u0438\u0442\u043e\u0432",
    "\u0438\u0442\u043f",
    "\u043d\u0430\u0441\u043e\u0441\u043d",
    "\u0441\u0435\u0440\u0432\u0435\u0440\u043d",
    "\u0433\u0440\u0449",
)
STOP_MARKERS = (
    "\u043b\u0438\u0441\u0442", "\u043c\u0430\u0441\u0448\u0442\u0430\u0431", "\u0433\u043e\u0441\u0442",
    "\u0434\u0430\u0442\u0430", "\u043f\u043e\u0434\u043f", "\u0438\u043d\u0432",
    "\u0438\u0442\u043e\u0433\u043e", "\u0432\u0441\u0435\u0433\u043e",
    "\u043e\u043a \u0441\u0437", "\u043e\u043a \u0441\u0432", "\u043e\u043a \u044e\u0437", "\u043e\u043a \u044e\u0432",
)


def _detect_floor_from_code_and_text(code: str, page_text: str = "") -> tuple[int, str]:
    digits_only = re.sub(r'^[^0-9]+', '', code or "")
    if len(digits_only.split(".")) == 3:
        first_ch = digits_only
        if first_ch == "0":
            return 0, "\u041f\u043e\u0434\u0432\u0430\u043b / \u0426\u043e\u043a\u043e\u043b\u044c (0xx)"
        if first_ch.isdigit() and int(first_ch) in range(1, 9):
            n = int(first_ch)
            return n, f"{n}-\u0439 \u044d\u0442\u0430\u0436 ({n}xx)"
    m_fl = re.search(r'(\d)[\-\s]*\u0439\s*\u044d\u0442\u0430\u0436', page_text or "", re.I)
    if m_fl:
        n = int(m_fl.group(1))
        return n, f"{n}-\u0439 \u044d\u0442\u0430\u0436"
    return 1, "1-\u0439 \u044d\u0442\u0430\u0436"


def build_building_twin_index() -> dict:
    rooms_by_code = {}
    pages = ParsedPage.objects.select_related("document").order_by("document_id", "page_number")[:300]

    for pg in pages:
        clean_txt = fix_autocad_mojibake(pg.text or "")
        matches = [(m.group(1), m.group(2), m.group(3), "R1/2") for m in RE_MODE_1_2.finditer(clean_txt)]
        matches += [(m.group(1), m.group(2), m.group(3), "R3") for m in RE_MODE_3.finditer(clean_txt)]

        for raw_code, raw_name, raw_area, mode_tag in matches:
            code = raw_code.strip()
            name = re.sub(r'\s+', ' ', raw_name).strip(" -.,:")
            area = float(raw_area.replace(",", "."))
            low_n = name.lower()
            if len(name) < 3 or area <= 0.5 or area > 5000:
                continue
            if any(bad in low_n for bad in STOP_MARKERS):
                continue

            floor_num, floor_label = _detect_floor_from_code_and_text(code, clean_txt[:400])
            cap_match = re.search(r'\(\u0434\u043e\s*(\d+)\s*\u0447\u0435\u043b', name, re.I)
            capacity = int(cap_match.group(1)) if cap_match else None
            is_tech = any(tk in low_n for tk in TECH_ROOMS_KEYWORDS)

            entry = rooms_by_code.setdefault(code, {
                "code": code, "name": name, "area_m2": area,
                "floor_num": floor_num, "floor_label": floor_label,
                "capacity": capacity, "is_tech": is_tech, "mode": mode_tag, "pages": [],
            })
            if len(name) > len(entry["name"]):
                entry["name"] = name
            if capacity and not entry["capacity"]:
                entry["capacity"] = capacity
            page_ref = {"doc_id": pg.document_id, "doc_title": pg.document.title if pg.document else "", "page_number": pg.page_number}
            if page_ref not in entry["pages"]:
                entry["pages"].append(page_ref)

    floors_map = {}
    for rm in sorted(rooms_by_code.values(), key=lambda x: (x["floor_num"], x["code"])):
        fl = floors_map.setdefault(rm["floor_label"], {"floor_num": rm["floor_num"], "floor_label": rm["floor_label"], "rooms": [], "total_area": 0.0})
        fl["rooms"].append(rm)
        fl["total_area"] = round(fl["total_area"] + rm["area_m2"], 2)

    return {"total_rooms": len(rooms_by_code), "floors": list(floors_map.values()), "rooms_map": rooms_by_code}


def build_single_room_passport(room_code: str) -> dict:
    twin = build_building_twin_index()
    rc = (room_code or "").strip()
    fl_num, fl_lbl = _detect_floor_from_code_and_text(rc)
    room_info = twin["rooms_map"].get(rc) or {
        "code": rc, "name": f"\u041f\u043e\u043c\u0435\u0449\u0435\u043d\u0438\u0435 {rc}", "area_m2": 0.0,
        "floor_num": fl_num, "floor_label": fl_lbl, "capacity": None, "is_tech": False, "pages": [],
    }
    all_pages = []
    for pg in ParsedPage.objects.select_related("document").filter(text__contains=rc).order_by("document__title", "page_number")[:30]:
        txt = fix_autocad_mojibake(pg.text or "")
        idx = txt.find(rc)
        snippet = re.sub(r'\s+', ' ', txt[max(0, idx - 60): idx + 140]).strip() if idx >= 0 else ""
        all_pages.append({"doc_id": pg.document_id, "doc_title": pg.document.title if pg.document else "", "page_number": pg.page_number, "snippet": snippet})

    related_reqs = list(PurchaseRequest.objects.filter(room_info__icontains=rc).values("id", "discipline", "material_name", "required_qty", "unit", "status")[:25])
    return {"room": room_info, "pages": all_pages, "requests": related_reqs}
