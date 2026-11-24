# -*- coding: utf-8 -*-
import math
import re
from decimal import Decimal
from storage_control.models import PartnerVendorLead, BimCrossLink
from storage_control.services.smart_router import is_noise_for_document, detect_document_profile


def _recover_real_qty_and_zone(req, clean_title: str) -> tuple[float | None, str]:
    """
    Находит строку прибора в тексте страницы PDF (ParsedPage), маскирует децимальные коды
    (АЦДР.425533.01) и индексы моделей (DTM 1217, РИП-24-4/40, АБ 1240) и забирает:
    1) настоящее количество штук, стоящее после якоря 'шт / компл';
    2) реальное помещение / зону, указанную в подзаголовке раздела выше по странице.
    """
    doc = getattr(req, "document", None)
    if not doc or not hasattr(doc, "pages"):
        return None, ""

    key_match = re.search(r'(?:Сириус|DTM\s*\d+|РИП-\d+|АБ\s*\d+|ИП\s*212[^\s,]*|[А-ЯЁA-Z]{4,})', clean_title)
    needle = key_match.group(0).lower() if key_match else clean_title[:14].lower()
    if len(needle) < 3:
        return None, ""

    real_qty = None
    detected_zone = ""
    room_re = re.compile(
        r'((?:помещени[ея]|серверн\w*|машинн\w*\s+зал\w*|пожарн\w*\s+пост\w*|диспетчерск\w*|электрощитов\w*|коридор\w*|цод)[^\n;]{0,45})',
        re.IGNORECASE,
    )

    for page in doc.pages.all().order_by("page_number"):
        txt = page.text or ""
        if needle not in txt.lower():
            continue

        lines = txt.splitlines()
        for idx, ln in enumerate(lines):
            if needle in ln.lower():
                context_above = "\n".join(lines[max(0, idx - 12) : idx + 1])
                rm = room_re.findall(context_above)
                if rm:
                    detected_zone = re.sub(r'\s+', ' ', rm[-1]).strip(" .:-")

                window = " ".join(lines[idx : min(len(lines), idx + 3)])
                masked = re.sub(r'[А-ЯЁA-Z]{2,6}\.\d{5,6}(?:\.\d+)?', ' CODE ', window)
                masked = re.sub(r'(?:DTM|АБ|РИП|ИП|ДИП|С2000)[\s\-]*\d+(?:[\-/]\d+)*', ' MODEL ', masked, flags=re.IGNORECASE)
                masked = re.sub(r'\d+\s*[ВV]\s*/\s*\d+\s*Ач', ' SPEC ', masked, flags=re.IGNORECASE)

                m_after = re.search(r'\b(?:шт|компл)\.?\s+(\d{1,4}(?:[\.,]\d+)?)\b', masked, re.IGNORECASE)
                if m_after:
                    val = float(m_after.group(1).replace(",", "."))
                    if 0 < val <= 2000:
                        real_qty = val
                        break
        if real_qty is not None or detected_zone:
            break

    return real_qty, detected_zone


def _humanize_and_group_item(raw_name: str, old_group: str, raw_qty: float = 0.0) -> tuple[str, str]:
    """Очищает обрывки, восстанавливает децимальные коды СПА/АПС и распределяет по инженерным подгруппам."""
    name = (raw_name or "").strip()
    name = re.sub(r'^\d{1,2}(?:\.\d{1,2})?\s+(?=[А-ЯЁA-Z])', '', name)
    name = re.sub(r'[\s,;]+L\s*=\s*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\.\s*0[\.,]\d+\s*$', '', name)
    if ')' in name and '(' not in name:
        name = name.replace(')', '').strip()

    if name.endswith("АЦДР.") and raw_qty > 100000:
        name = f"{name}{raw_qty:.2f}"
    if name.endswith("/") and 1 <= raw_qty <= 999 and abs(raw_qty - int(raw_qty)) < 1e-6:
        name = f"{name}{int(raw_qty)}"

    name = re.sub(r'^(\d{2,3}\s*[xх×]\s*\d{1,2}\s+ГОСТ\s*103-2006)', r'Полоса стальная \1', name, flags=re.IGNORECASE)
    name = re.sub(r'^аналог\*\)\s*на\s+цементном\s+вяжущем', 'Блок строительный на цементном вяжущем (аналог по РД)', name, flags=re.IGNORECASE)
    name = re.sub(r'^шпатлевка\b', 'Шпатлёвка финишная', name, flags=re.IGNORECASE)
    if name.lower().startswith('упругая прокладка'):
        name = 'Упругая звукоизоляционная прокладка (базальтовая основа γ=55 кг/м³)'

    name = re.sub(r'\b1\s*тр\.\s*ПНД\b', 'Труба ПНД (защитный футляр, 1 нитка)', name, flags=re.IGNORECASE)
    name = re.sub(r'\b2\s*тр\.\s*ПЭ\b', 'Труба ПЭ (защитный футляр, 2 нитки)', name, flags=re.IGNORECASE)
    name = re.sub(r'\b1\s*тр\.\s*ПЭ\b', 'Труба ПЭ (защитный футляр, 1 нитка)', name, flags=re.IGNORECASE)

    low = name.lower()
    if any(w in low for w in ('ппку', 'сириус', 'ацдр', 'с2000', 'бриз', 'модуль релейн', 'контроллер')):
        grp = "[04.1 СПА/АПС · Приборы ППКУ и Управление]"
    elif any(w in low for w in ('рип-24', 'блок питания', 'аккумулятор', 'dtm 1217', 'аб 1240', 'ибп')):
        grp = "[04.2 СПА/АПС · Питание РИП и Аккумуляторы]"
    elif any(w in low for w in ('извещател', 'дип-34', 'ипр', 'оповещател', 'табло', 'сирена')):
        grp = "[04.3 СПА/АПС · Извещатели и Оповещатели]"
    elif any(w in low for w in ('кпснг', 'frls', 'frhf', 'огнестойк', 'мастика', 'сэ-611', 'окl', 'огнезащит', 'пистолет монтажный')):
        grp = "[04.4 СПА/АПС · Кабель огнестойкий FRLS]"
    elif any(w in low for w in ('бордюр', 'брусчат', 'плитк', 'асфальт', 'газон')):
        grp = "[02. Благоустройство и Дороги]"
    elif any(w in low for w in ('гост 8509', 'гост 103', 'уголок', 'полоса', 'швеллер', 'арматур', 'анкер')):
        grp = "[02. Металл, Крепёж и ЖБИ]"
    elif any(w in low for w in ('пазогребнев', 'шпатлевк', 'шпатлёвк', 'герметик', 'прокладк', 'штукатур', 'краск')):
        grp = "[03. Отделка и Изоляция]"
    elif any(w in low for w in ('блок строительный', 'газобетон', 'бетон', 'цемент', 'щебен', 'песок')):
        grp = "[01. Инертные, Грунт и Бетон]"
    elif any(w in low for w in ('труб', 'пнд', 'пэ ', 'выпуск к1', 'футляр', 'канализац', 'водопровод')):
        grp = "[05. Наружные сети и Футляры]"
    elif any(w in low for w in ('кабел', 'пвбшв', 'апвбшв', 'ввг', 'авбшв', 'щит', 'вру', 'автомат', 'клемма', 'наконечник', 'профиль монтажный', 'tsc ')):
        grp = "[03. Электроснабжение и Кабели]"
    else:
        grp = old_group or "[07. Общестроительные ТМЦ]"
    return name, grp


def _calc_construction_schedule(qty_val: float, u_val: str, m_name: str) -> tuple[str, str]:
    """Возвращает нормализованную единицу ОКЕИ (пог. м) и расчёт смен/звена по ЕНиР."""
    m_low = (m_name or "").lower()
    n_unit = "пог. м" if u_val.strip() == "м" and any(
        w in m_low for w in ("бордюр", "труб", "кабел", "лоток", "пнд", "пэ ", "пвбшв", "апвбшв", "ввг", "выпуск", "герметик")
    ) else u_val

    if "бордюр" in m_low:
        rate, crew = 40.0, "звено 3 дор. рабочих"
    elif any(w in m_low for w in ("труб", "пнд", "пэ ", "выпуск", "футляр")):
        rate, crew = 50.0, "звено 2 монтажника НВК"
    elif any(w in m_low for w in ("кабел", "пвбшв", "апвбшв", "ввг", "лоток", "профиль монтажный")):
        rate, crew = 180.0, "звено 4 электромонтажника"
    elif any(w in m_low for w in ("пазогребнев", "блок строительный", "газобетон")):
        rate, crew = 18.0, "звено 2 каменщика"
    elif any(w in m_low for w in ("шпатлёвк", "шпатлевк", "краск", "штукатур")):
        rate, crew = 45.0, "звено 2 отделочника"
    elif u_val in ("м3", "м³"):
        rate, crew = 22.0, "звено 4 бетонщика"
    else:
        rate, crew = 15.0, "звено 2 монтажника"

    shifts = max(1, math.ceil(qty_val / rate))
    return n_unit, f"{shifts} смен (по 8 ч) · {crew} (норма {int(rate)} {n_unit}/см.)"


def _sanitize_elevation_and_room(floor_info: str, room_info: str, detected_zone: str, is_spa: bool) -> str:
    """Отсекает фейковые отметки из децимальных кодов (425533.006) и подставляет реальную зону/помещение."""
    f_raw = (floor_info or "").strip()
    valid_elev = ""
    if f_raw and f_raw not in ("24.045", "59.133", "24.0454"):
        m = re.match(r'^([\+\-]?\d+(?:[\.,]\d+)?)', f_raw)
        if m:
            try:
                num = float(m.group(1).replace(",", "."))
                if -30.0 <= num <= 150.0:
                    valid_elev = f"Отм. {f_raw}"
            except ValueError:
                pass
        else:
            valid_elev = f_raw

    room_clean = (room_info or "").strip() or detected_zone
    if not room_clean and is_spa:
        room_clean = "ЦОД · Зона оборудования СПА"

    return f"{valid_elev} {room_clean}".strip() or "По плану РД"


def build_engineering_procurement_rows(requests_qs) -> list:
    """Объединяет дубли в Ведомости закупок, восстанавливает количества СПА/АПС и группирует по узлам."""
    bim_links = list(BimCrossLink.objects.all())
    vendor_leads = list(PartnerVendorLead.objects.all())
    grouped = {}

    for req in requests_qs:
        if req.node_cabinet and req.node_cabinet.startswith("[B2B-ПАРТНЁР]"):
            continue

        raw_m = (req.material_name or "").strip()
        doc_title = req.document.title if getattr(req, "document", None) else ""
        if is_noise_for_document(doc_title, raw_m):
            continue

        low_m = raw_m.lower()
        if (
            len(raw_m) < 8
            or re.match(r'^(?:каждые|не\s+менее|не\s+более|не\s+больше|наименование\b|итого\b|всего\b|менее\s+\d)', low_m)
            or re.search(
                r'(?:^сп\s+\d|п\.\s*\d+\.\d+|спецификация\s+оборудования.*листов|dk[cс]-2018\.[a-z]\d|высота\s+(?:пространства|от\s+фальшпола)|макс\.\s*нагрузка|не\s+(?:менее|более|больше|допускаются)|пропускная\s+способность|при\s+глубине|водосборного\s+приямка|протяженностью|γ\s*=|г/м|допустимая\s+нагрузка|\d{3,4}\s*[xх×]\s*$)',
                low_m,
            )
        ):
            continue

        if re.match(r'^РИП-24\s*\(', raw_m, re.IGNORECASE):
            continue

        half = len(raw_m) // 2
        if half > 15 and raw_m[:half].strip() == raw_m[half:].strip():
            raw_m = raw_m[:half].strip()
        raw_m = re.sub(r'\s*\([^\)]*$', '', raw_m).strip()

        raw_qty_f = float(req.required_qty)
        clean_title, clean_group = _humanize_and_group_item(raw_m, req.node_cabinet, raw_qty=raw_qty_f)

        clean_unit = req.unit
        qty_f = raw_qty_f
        detected_zone = ""
        is_spa = "[04." in clean_group

        if is_spa:
            clean_unit = "шт"
            qty_int_str = str(int(round(qty_f)))
            if qty_f > 5000 or (len(qty_int_str) >= 2 and qty_int_str in clean_title):
                recovered_qty, detected_zone = _recover_real_qty_and_zone(req, clean_title)
                qty_f = recovered_qty if recovered_qty is not None else 1.0

        rec_type = "BUY" if "упругая звукоизоляционная прокладка" in clean_title.lower() else req.record_type
        rec_display = "🛒 Закупка ТМЦ" if rec_type == "BUY" else req.get_record_type_display()

        key = (rec_type, clean_title.lower(), clean_unit.lower())

        if key not in grouped:
            low = clean_title.lower()
            if any(w in low for w in ('труб', 'пнд', 'пэ ', 'футляр')):
                sticks = max(1, math.ceil((qty_f + 1.0) / 6.0))
                pack_hint = f"Кратность: {sticks} хлыст. × 6 м ({sticks * 6} м)"
            elif any(w in low for w in ('кабел', 'пвбшв', 'апвбшв', 'ввг')):
                with_res = round(qty_f * 1.05, 1)
                drums = max(1, math.ceil(with_res / 250.0))
                pack_hint = f"С запасом +5%: {with_res} м ({drums} барабан. × 250 м)"
            elif 'бордюр' in low:
                pallets = max(1, math.ceil(qty_f / 18.0))
                pack_hint = f"~{int(math.ceil(qty_f))} шт. (~{pallets} подд.)"
            elif 'герметик' in low:
                tubes = max(1, math.ceil((qty_f * 0.12) / 0.6))
                pack_hint = f"Расход ~{tubes} туб (по 600 мл)"
            elif 'пазогребнев' in low:
                plates = max(1, math.ceil(qty_f / 0.333))
                pack_hint = f"~{plates} плит (667×500×100 мм)"
            else:
                pack_hint = ""

            bim_badge, bim_level = "", "ok"
            for bl in bim_links:
                if ('110' in clean_title and '110' in bl.bim_tag) or ('160' in clean_title and '160' in bl.bim_tag) or ('5х185' in clean_title and '5х185' in bl.bim_tag):
                    bim_badge = bl.engineering_note[:115]
                    bim_level = "warn" if bl.link_status == "COLLISION" else "ok"
                    break

            vendor_badge = ""
            for vl in vendor_leads:
                if any(w in (vl.category_group + " " + vl.project_materials).lower() for w in low.split()[:2]):
                    vendor_badge = f"🤝 Заложен поставщик: «{vl.vendor_name}» ({vl.region})"
                    break

            norm_unit, real_schedule = _calc_construction_schedule(qty_f, clean_unit, clean_title)
            final_qty_dec = Decimal(str(round(qty_f, 2)))
            stock_dec = max(Decimal("0"), req.required_qty - req.deficit_qty) if raw_qty_f == qty_f else Decimal("0")
            deficit_dec = max(Decimal("0"), final_qty_dec - stock_dec)

            grouped[key] = {
                "id": req.id,
                "doc_id": req.document_id or 0,
                "record_type": rec_type,
                "record_type_display": rec_display,
                "location": _sanitize_elevation_and_room(req.floor_info, req.room_info, detected_zone, is_spa),
                "material_name": clean_title,
                "node_cabinet": clean_group,
                "unit": norm_unit,
                "schedule_hint": real_schedule,
                "required_qty": final_qty_dec,
                "stock_qty": stock_dec,
                "deficit_qty": deficit_dec,
                "pack_hint": pack_hint,
                "bim_badge": bim_badge,
                "bim_level": bim_level,
                "vendor_badge": vendor_badge,
                "assigned_itr": req.responsible_itr or "ПТО Штаб",
                "status_display": req.get_status_display(),
            }
        else:
            add_qty = Decimal(str(round(qty_f, 2)))
            grouped[key]["required_qty"] += add_qty
            grouped[key]["deficit_qty"] += add_qty


    # Автоматическая распаковка составов ОКЛ (Огнестойких кабельных линий) из фигурных скобок {...}
    extra_okl_rows = []
    for item in list(grouped.values()):
     m_okl = re.search(r'компоненты\s*:\s*\{([^\}]+)\}', item["material_name"], re.IGNORECASE)
     if not m_okl:
         continue
     for part in m_okl.group(1).split("+"):
         pm = re.match(r'^(.+?)\s*[\-–—]\s*(\d+(?:[\.,]\d+)?)\s*(м|шт|компл|упак)\b', part.strip(), re.IGNORECASE)
         if pm:
             sub_name = f"↳ [В составе ОКЛ] {pm.group(1).strip()}"
             sub_qty = Decimal(pm.group(2).replace(",", "."))
             sub_unit = pm.group(3).lower()
             _, sub_sched = _calc_construction_schedule(float(sub_qty), sub_unit, sub_name)
             extra_okl_rows.append({
                 **item,
                 "material_name": sub_name,
                 "unit": sub_unit,
                 "required_qty": sub_qty,
                 "stock_qty": Decimal("0"),
                 "deficit_qty": sub_qty,
                 "schedule_hint": sub_sched,
                 "pack_hint": "Авто-разузлование ОКЛ по ГОСТ Р 53316",
             })

    all_rows = list(grouped.values()) + extra_okl_rows
    return sorted(all_rows, key=lambda item: (item["node_cabinet"], item["id"]))
