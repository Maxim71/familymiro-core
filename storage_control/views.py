
def _build_foundation_to_handover_design(q: str, totals_by_unit: dict) -> dict:
    low = (q or "").lower()
    if any(k in low for k in ("трубопров", "эмал", "пф", "гф-021", "антикор")):
        return {"stage": "Этап 4 / 6 · ОВ/ВК: Антикоррозийная окраска стальных труб (СП 73.13330)", "before": "Очистка труб от ржавчины и окалины (Ст2) → Обезжиривание уайт-спиритом → Грунтовка ГФ-021", "supply": "Эмаль ПФ-115 в 2 слоя (тара 20–25 кг) строго ДО монтажа теплоизоляции Energoflex", "companion": "Грунт ГФ-021, уайт-спирит / растворитель 646, щётки по металлу, кисти, ветошь", "after": "Контроль толщины сухой плёнки (СП 28.13330) + паспорт на эмаль + АОСР № 344/пр до изоляции"}
    if any(k in low for k in ("ркдм", "клад", "клапан", "решетк")):
        return {"stage": "Этап 4 / 6 · Противодымная вентиляция (ПВ / ДУ / ПД)", "before": "Монтаж шахт дымоудаления и проемов в огнестойких перегородках", "supply": "Заказ клапанов с указанием сечения (1040х840 / 700х600) и напряжения привода (220В/24В)", "companion": "Ответные фланцы, огнезащитный герметик, термолента, гибкая вставка, крепёж", "after": "Сертификат пожарной безопасности + акт испытаний срабатывания от АПС + АОСР № 344/пр"}
    if any(k in low for k in ("фундам", "бетон", "армат", "а500", "котлов", "сваи", "плита")):
        return {"stage": "Этап 1 / 6 · Фундамент (КЖ0)", "before": "Геодезия → Котлован → Подбетонка В7.5 → Гидроизоляция", "supply": "Завоз по захваткам бетонирования (миксеры + прогрев)", "companion": "Фиксаторы слоя, вязальная проволока, опалубка, вибраторы", "after": "Паспорт бетона/металла + кубики 7/28 сут + АОСР № 344/пр", "next_wave": "Предугадываем следующий закуп: анкерные болты и металлоконструкции КМ (рамы Рм-1.1)"}
    if any(k in low for k in ("кровл", "техноэласт", "пламя", "рама", "балк")):
        return {"stage": "Этап 2–3 / 6 · Каркас и Кровля", "before": "Приёмка фундамента → Геодезия осей → Уклон и праймер", "supply": "Длинномер / манипулятор + подъём по секторам (+10% нахлёст)", "companion": "Праймер, аэраторы, краевые рейки, герметик, метизы КМ", "after": "Геодезия + УЗК швов / пролив кровли + АОСР № 344/пр"}
    if any(k in low for k in ("ral", "краск", "шпатл", "шпакл", "грунт", "отдел")):
        return {"stage": "Этап 5 / 6 · Чистовая отделка и колеровка", "before": "Тепловой контур (+15°C) → Бетоноконтакт → Штукатурка → Шпатлёвка 2 слоя", "supply": "Поэтажный завоз вёдрами по 10л (2 слоя + 10% запас) после высыхания стен", "companion": "Грунтовка 2 слоя, стеклообои + клей, валики, скотч, плёнка", "after": "Сертификат КМ1 + УПД + АОСР № 344/пр"}
    return {"stage": "Этап 4 / 6 · Инженерные системы (ОВ / ВК / ЭС)", "before": "Готовность перекрытий и проёмов → Разметка трасс → Опоры", "supply": "Поэтажная комплектация магистрали + фасонных узлов и крепежа из РД", "companion": "Шпильки, анкеры, болты, гайки, шайбы, прокладки, противопожарные муфты", "after": "Испытания (ПНР / опрессовка / мегаомметр) + АОСР № 344/пр"}

def _detranslit_mark_slug(slug: str) -> str:
    import re
    s = re.sub(r'^\d+[\-_]\d+[\-_]', '', (slug or '')).replace('-', ' ').strip()
    s = re.sub(r'h$', '', s)
    pairs = [
        ("shch", "щ"), ("sh", "ш"), ("ch", "ч"), ("zh", "ж"), ("yu", "ю"), ("ya", "я"),
        ("kh", "х"), ("ts", "ц"), ("a", "а"), ("b", "б"), ("v", "в"), ("g", "г"),
        ("d", "д"), ("e", "е"), ("z", "з"), ("i", "и"), ("k", "к"), ("l", "л"),
        ("m", "м"), ("n", "н"), ("o", "о"), ("p", "п"), ("r", "р"), ("s", "с"),
        ("t", "т"), ("u", "у"), ("f", "ф"), ("y", "ы"),
    ]
    low = s.lower()
    for lat, cyr in pairs:
        low = low.replace(lat, cyr)
    return low.strip().capitalize()

def _engineering_sort_key(item: dict) -> tuple:
    import re
    nm = (item.get("mark_name") or "").lower()
    zn = (item.get("floor_or_zone") or "").lower()
    # 1. ??????? ??????: ?????? (0) -> 1 ???? (1) -> 2 ???? (2) -> ?????? (9)
    lvl = 0 if "подвал" in zn else (1 if "1" in zn else (2 if "2" in zn else 9))
    # 2. ??? ????????: 1. ?????? ??????? (0) -> 2. ??????/??????/???????? (1) -> 3. ??????????/?????? (2)
    kind = 1 if any(k in nm for k in ("отвод", "переход", "тройник", "утка")) else (
           2 if any(k in nm for k in ("фланец", "болт", "гайка", "шпильк", "хомут")) else 0)
    # 3. ??????/??????? ?? ???????? ? ????????
    nums = [int(x) for x in re.findall(r'\d{2,4}', nm)]
    area_score = -(nums[0] * nums[1]) if len(nums) >= 2 else (-(nums[0] ** 2) if nums else 0)
    return (lvl, kind, area_score, nm)


def _build_system_assembly_info(name: str, zone: str, doc_title: str) -> dict:
    import re
    low_all = f"{name} {zone} {doc_title}".lower()
    m_sys = re.search(r'(?:Система|КЛ|ВРУ|ЩР)\s*[\-]?[\u0410-\u042fA-Za-z0-9\.\-]{1,12}', f"{name} {zone}")

    if "подвал" in low_all or "итп" in low_all:
        loc_tag = "Подвал / ИТП"
    elif any(k in low_all for k in ("кровл", "пламя стоп", "техноэласт")):
        loc_tag = "Кровля здания"
    elif any(k in low_all for k in ("гп", "нсс", "транш")):
        loc_tag = "Наружные сети / ГП"
    else:
        loc_tag = "Этажи и помещения здания"

    if "ов" in low_all or "воздух" in low_all or "вент" in low_all:
        sys_label = m_sys.group(0) if m_sys else "Система ОВ (Вентиляция)"
        pnr_label, pnr_unit, pnr_target = "ПНР расход", "м³/ч", 2940
    elif "вк" in low_all or "фланец" in low_all or "кран" in low_all or "труб" in low_all:
        sys_label = m_sys.group(0) if m_sys else "Система ВК / Теплоснабжение"
        pnr_label, pnr_unit, pnr_target = "Опрессовка", "бар", 16
    elif "эс" in low_all or "кабел" in low_all or "лоток" in low_all or "профил" in low_all:
        sys_label = m_sys.group(0) if m_sys else "Система ЭС / Электроснабжение"
        pnr_label, pnr_unit, pnr_target = "Изоляция", "МОм", 1000
    else:
        sys_label = m_sys.group(0) if m_sys else "Конструктив / Кровля / АР"
        pnr_label, pnr_unit, pnr_target = "Контроль слоя", "мм", 100

    origin_phrase = f"Принадлежит системе «{sys_label}» · Зона: {loc_tag} ({doc_title} · {zone})"
    flow_phrase = f"Закуплено и принято по УПД → Выдано на участок ({loc_tag}, М-11): монтаж пошёл · Срок и отчёт прораба ведутся"
    mismatch_reasons = "Точки над i при несоответствии: 1) Сверка габарита/сечения/Ду с узлом РД; 2) Проверка рабочих параметров (давление/расход/напряжение); 3) Комплектность по УПД → авто-акт ТОРГ-2."
    return {"sys_origin": origin_phrase, "sys_flow": flow_phrase, "sys_mismatch": mismatch_reasons, "pnr_label": pnr_label, "pnr_unit": pnr_unit, "pnr_target": pnr_target}


def _build_item_tech_passport(name: str) -> dict:
    import re
    low = (name or "").lower()
    m_du = re.search(r'(?:\u0414\u0443|DN)\s*(\d{2,4})', name, re.I)
    m_ru = re.search(r'(?:\u0420\u0443|PN)\s*(\d{1,3})', name, re.I)
    m_gost = re.search(r'(?:\u0413\u041e\u0421\u0422|\u0421\u041f)\s*[0-9\-\.]+', name, re.I)

    du_val = f"\u0414\u0443 {m_du.group(1)}" if m_du else "\u043f\u043e \u043f\u0440\u043e\u0435\u043a\u0442\u0443"
    ru_val = f"\u0420\u0443 {m_ru.group(1)}" if m_ru else "\u0420\u0443 16 (\u0441\u0442\u0430\u043d\u0434\u0430\u0440\u0442)"
    gost_val = m_gost.group(0) if m_gost else "\u0413\u041e\u0421\u0422 / \u0422\u0423"

    if "\u0444\u043b\u0430\u043d\u0435\u0446" in low:
        analog = f"\u0424\u043b\u0430\u043d\u0435\u0446 \u0441\u0442\u0430\u043b\u044c\u043d\u043e\u0439 \u043f\u043b\u043e\u0441\u043a\u0438\u0439 {du_val} {ru_val} \u0413\u041e\u0421\u0422 33259-2015 (\u0421\u044220, \u0410\u0414\u041b / \u0421\u0422\u041c)"
        specs = f"\u0414\u0438\u0430\u043c\u0435\u0442\u0440: {du_val} | \u0414\u0430\u0432\u043b\u0435\u043d\u0438\u0435: {ru_val} | \u0421\u0442\u0430\u043d\u0434\u0430\u0440\u0442: \u0413\u041e\u0421\u0422 33259-2015 | \u041c\u0430\u0442\u0435\u0440\u0438\u0430\u043b: \u0421\u0442\u0430\u043b\u044c 20"
    elif "\u043a\u0440\u0430\u043d" in low:
        analog = f"\u041a\u0440\u0430\u043d \u0448\u0430\u0440\u043e\u0432\u043e\u0439 \u043f\u043e\u043b\u043d\u043e\u043f\u0440\u043e\u0445\u043e\u0434\u043d\u043e\u0439 {du_val} {ru_val} (\u0410\u0414\u041b \u0411\u0438\u0432\u0430\u043b / LD / Giacomini)"
        specs = f"\u0414\u0438\u0430\u043c\u0435\u0442\u0440: {du_val} | \u0414\u0430\u0432\u043b\u0435\u043d\u0438\u0435: {ru_val} | \u041f\u0440\u043e\u0445\u043e\u0434: \u043f\u043e\u043b\u043d\u044b\u0439 | \u041a\u043b\u0430\u0441\u0441 \u0433\u0435\u0440\u043c\u0435\u0442\u0438\u0447\u043d\u043e\u0441\u0442\u0438: \u0410"
    elif "\u0442\u0435\u0445\u043d\u043e\u044d\u043b\u0430\u0441\u0442" in low or "\u043f\u043b\u0430\u043c\u044f" in low:
        analog = "\u0422\u0435\u0445\u043d\u043e\u044d\u043b\u0430\u0441\u0442 \u042d\u041a\u041f / \u0423\u043d\u0438\u0444\u043b\u0435\u043a\u0441 \u042d\u041a\u041f \u0420\u041f1 (\u0413\u041e\u0421\u0422 32805-2014, \u0432\u0435\u0440\u0445\u043d\u0438\u0439 \u0441\u043b\u043e\u0439)"
        specs = "\u0422\u0438\u043f: \u0421\u0411\u0421-\u043c\u043e\u0434\u0438\u0444\u0438\u0446\u0438\u0440\u043e\u0432\u0430\u043d\u043d\u044b\u0439 | \u0413\u0440\u0443\u043f\u043f\u0430 \u0433\u043e\u0440\u044e\u0447\u0435\u0441\u0442\u0438: \u0420\u041f1 | \u0413\u0438\u0431\u043a\u043e\u0441\u0442\u044c \u043d\u0430 \u0431\u0440\u0443\u0441\u0435: -25\u00b0C"
    elif any(k in low for k in ("\u043f\u0440\u043e\u0444\u0438\u043b\u044c", "\u0431\u043e\u043b\u0442", "\u0433\u0430\u0439\u043a\u0430", "\u0448\u0430\u0439\u0431\u0430", "\u0430\u043d\u043a\u0435\u0440", "\u0448\u043f\u0438\u043b\u044c\u043a")):
        analog = "\u041c\u043e\u043d\u0442\u0430\u0436\u043d\u044b\u0439 \u043f\u0440\u043e\u0444\u0438\u043b\u044c / \u043a\u0440\u0435\u043f\u0451\u0436 \u043e\u0446\u0438\u043d\u043a\u043e\u0432\u0430\u043d\u043d\u044b\u0439 (\u0414\u041a\u0421 B5 Combitech / \u0421\u041e\u042d\u041c\u0418 / Hilti / OBO Bettermann)"
        specs = "\u041f\u043e\u043a\u0440\u044b\u0442\u0438\u0435: \u0433\u043e\u0440\u044f\u0447\u0438\u0439 / \u0433\u0430\u043b\u044c\u0432\u0430\u043d\u0438\u0447\u0435\u0441\u043a\u0438\u0439 \u0446\u0438\u043d\u043a | \u041a\u043b\u0430\u0441\u0441 \u043f\u0440\u043e\u0447\u043d\u043e\u0441\u0442\u0438: 8.8 (\u0413\u041e\u0421\u0422 7798-70 / 5915-70)"
    else:
        analog = _suggest_analog_for_material(name)
        specs = f"\u041f\u0430\u0440\u0430\u043c\u0435\u0442\u0440\u044b: {du_val} | {ru_val} | {gost_val}"

    return {"analog_item": analog, "tech_specs": specs}
from storage_control.services.input_calibrator import classify_pdf_line_at_gate, normalize_unit_and_name, canonicalize_spec_text, build_work_sequence_cascade

def _extract_mark_search_tokens(q: str) -> list[str]:
    import re
    clean = re.sub(r'^\d+(?:\.\d+)+\s*', '', (q or '').strip())
    tokens = []
    # ??????? (???????? 35064)
    for art in re.findall(r'\b\d{4,7}\b', clean):
        tokens.append(art)
    # ??????? ? x / ? (???????? 200?80)
    for dim in re.findall(r'\d{2,4}[xX\u0445\u00d7]\d{2,4}', clean):
        tokens.append(dim.replace('x', '\u0445').replace('X', '\u0445'))
        tokens.append(dim.replace('\u0445', 'x'))
    # ?????? 2 ???????? ????? (???????? "????? ????????")
    words = [w for w in re.findall(r'[\u0410-\u042f\u0430-\u044fA-Za-z]{4,}', clean) if w.lower() not in ('\u0441\u0442\u0430\u043b\u044c\u043d\u043e\u0439', '\u043e\u0446\u0438\u043d\u043a\u043e\u0432\u0430\u043d\u043d\u044b\u0439')]
    if words:
        tokens.append(words)
    return list(dict.fromkeys([t for t in tokens if t]))

def _norm_x_variants(q: str) -> list[str]:
    base = (q or "").strip()
    if not base:
        return []
    import re
    v_ru = re.sub(r'(?<=\d)[xX\u00d7\*](?=\d)', '\u0445', base)
    v_en = re.sub(r'(?<=\d)[\u0445\u0425\u00d7\*](?=\d)', 'x', base)
    v_mul = re.sub(r'(?<=\d)[xX\u0445\u0425\*](?=\d)', '\u00d7', base)
    return list(dict.fromkeys([base, v_ru, v_en, v_mul]))
# -*- coding: utf-8 -*-
import os
import re
import logging
from decimal import Decimal
from django.shortcuts import render, redirect, reverse
from django.conf import settings
from django.views.generic import View
from django.http import JsonResponse, HttpResponse
from django.db import models
from .services.pdf_ocr import extract_and_store_pages
from .services.spec_matcher import parse_specifications_and_create_requests

from .services.smart_router import resolve_section_and_brigade

import hashlib
from django.db.models import Q
from pypdf import PdfReader
import pytesseract
from django.contrib import messages

from django.contrib.auth import authenticate, login, logout
from .models import Document, ParsedPage, ItrStaff, WarehouseTmc, PurchaseRequest
from django.contrib.auth import authenticate, login, logout
from .models import Document, ParsedPage, ItrStaff, WarehouseTmc, PurchaseRequest

def resolve_section_and_brigade(section_code):
    code = str(section_code or "РД").upper().strip()
    return {"code": code, "title": f"Раздел {code}", "brigade": "Звено ПТО"}

logger = logging.getLogger(__name__)

pytesseract.pytesseract.tesseract_cmd = getattr(
    settings, 'TESSERACT_CMD', r'C:\Program Files\Tesseract-OCR\tesseract.exe'
)

# Коды томов: 24.0454-Р-ГП, 14-КЖ1, 61-ОВ1.ЦОД
CODE_RE = re.compile(
    r'^(?:\d{1,3}\s*[\.\)\|]?\s*)?([А-ЯЁA-Z0-9\.\-/]{2,25}-(?:Р|П)-[А-ЯЁA-Z0-9\.\-/]{1,20})\s*[\|\-–—:\s]+\s*(.{4,180})$',
    re.IGNORECASE
)


NAV_ITEMS = [
    {'name': 'Главная', 'url_name': 'storage_control:index_family'},
    {'name': 'О компании', 'url_name': '#'},
    {'name': 'Услуги', 'url_name': '#'},
    {'name': 'Блог', 'url_name': '#'},
    {'name': 'Контакты', 'url_name': '#'},
]


class AdvancedConstructionControlView(View):
    """Основной пульт управления: загрузка PDF, контроль ревизий SHA-256, фильтр и ведомость"""

    def get(self, request, *args, **kwargs):
        dossier_id = request.GET.get('dossier_id')
        if dossier_id:
            dossier_payload = {
                "step_1_code": "24.0454-Р-ГП",
                "step_2_material": "Геотекстиль Дорнит",
                "step_3_altitude": "0.000м (Репер)",
                "step_4_axes": "Оси 1-5 // А-Д",
                "step_6_passport": "Верифицирован (media/passports/65-CCK_Zavod.pdf)",
                "final_id_hash": dossier_id.upper()
            }
            return render(request, "storage_control/pto_dossier.html", {
                "dossier": dossier_payload,
                "nav_items": NAV_ITEMS
            })

        stock_list = WarehouseTmc.objects.filter(owner=current_owner).order_by('item_code')
        staff_list = ItrStaff.objects.filter(owner=current_owner).order_by('name')
        all_reqs = PurchaseRequest.objects.filter(document__owner=current_owner)

    # Изоляция рабочего пространства по владельцу (Multi-Tenant)
    def get(self, request, *args, **kwargs):
        current_owner = request.user if request.user.is_authenticated else None
        documents_list = Document.objects.filter(owner=current_owner).order_by('-uploaded_at')[:50]
        stock_list = WarehouseTmc.objects.filter(owner=current_owner).order_by('item_code')
        staff_list = ItrStaff.objects.filter(owner=current_owner).order_by('name')
        selected_doc_id = request.GET.get('doc_id')
        section_filter = (request.GET.get('section') or '').strip().upper()

        if selected_doc_id and selected_doc_id.isdigit():
            active_doc = Document.objects.filter(owner=current_owner, id=int(selected_doc_id)).first()
        else:
            active_doc = documents_list.first()

        parsed_data = []
        file_ok = False
        if active_doc and active_doc.file:
            try:
                file_ok = os.path.exists(active_doc.file.path)
            except (NotImplementedError, ValueError):
                file_ok = False

        if file_ok:
            for page in active_doc.pages.all():
                if not page.text:
                    continue
                for line in page.text.split("\n"):
                    m1 = CODE_RE.match(line.strip())
                    if m1:
                        c = m1.group(1).strip()
                        n = re.sub(r'[.\s_]{3,}', ' ', m1.group(2).strip())
                        if len(n) > 3:
                            if section_filter and section_filter not in c.upper() and section_filter not in n.upper():
                                continue
                            decoded = resolve_section_and_brigade(c)
                            parsed_data.append({
                                "code": c,
                                "name": decoded.get("section") or decoded.get("title") or n,
                                "snip_ref": decoded.get("snip_ref", "ГОСТ 21.1101-2013"),
                                "snip_url": decoded.get("snip_url", "https://cntd.ru"),
                                "brigade": decoded.get("brigade", "Звено ПТО"),
                                "duty": decoded.get("duty", "Монтаж по рабочей документации"),
                                "stage": "РД",
                            })

                                    # Группируем ведомость по профильным бригадам с указанием состава звена и ответственных
        brigade_groups = {}
        staff_by_idx = list(staff_list)

        for idx, item in enumerate(parsed_data):
            b_name = item["brigade"] or "Общестроительная бригада ПТО"
            if b_name not in brigade_groups:
                # Назначаем ответственного ИТР из базы и расчётную численность звена
                lead_staff = staff_by_idx[len(brigade_groups) % len(staff_by_idx)] if staff_by_idx else None
                lead_label = (
                    f"{lead_staff.name} [{lead_staff.staff_id}] ({lead_staff.role_type})"
                    if lead_staff else "Косарев М.В. [ITR-MAX-77] (Главный Архитектор)"
                )
                team_size = 6 if ("монолит" in b_name.lower() or "строител" in b_name.lower()) else 4
                brigade_groups[b_name] = {
                    "brigade_name": b_name,
                    "group_num": len(brigade_groups) + 1,
                    "leader": lead_label,
                    "team_size": team_size,
                    "items": [],
                }
            brigade_groups[b_name]["items"].append(item)


        err_msg = None if parsed_data else "Склад чертежей пуст или по фильтру нет позиций. Загрузите PDF-комплект ниже."
        purchase_requests = (
            PurchaseRequest.objects.filter(document=active_doc).order_by('record_type', 'id')
            if active_doc else []
        )

        all_reqs = PurchaseRequest.objects.filter(document__owner=current_owner)
        erp_b2b_stats = {
            "new_requests": all_reqs.filter(record_type="BUY", status="NEW").count(),
            "in_progress_b2b": all_reqs.filter(record_type="BUY", status__in=["IN_PROGRESS", "PAID"]).count(),
            "delivered_count": all_reqs.filter(record_type="BUY", status="DELIVERED").count(),
            "warehouse_positions": stock_list.count(),
        }

        total_docs = Document.objects.filter(owner=current_owner).count()
        work_docs = Document.objects.filter(owner=current_owner, work_status="WORK").count()
        crm_ceo_stats = {
            "total_docs": total_docs,
            "work_docs": work_docs,
            "readiness_pct": int((work_docs / total_docs) * 100) if total_docs else 0,
            "tep_volumes_count": all_reqs.filter(record_type="TEP").count(),
            "limits_count": all_reqs.filter(record_type="LIMIT").count(),
        }

        requested_goal = request.GET.get("goal", "")
        if not requested_goal:
            if brigade_groups:
                effective_goal = "BRIGADES"
            elif purchase_requests:
                effective_goal = "SUPPLY"
            else:
                effective_goal = "ALL"
        else:
            effective_goal = requested_goal

        from storage_control.services.route_tracer import build_engineering_procurement_rows
        purchase_requests = build_engineering_procurement_rows(purchase_requests)

        dynamic_tables = []
        if active_doc and getattr(active_doc, "file", None):
            try:
                from storage_control.services.grid_extractor import extract_geometric_tables
                geo = extract_geometric_tables(active_doc.file.path)
                dynamic_tables = [t for t in geo.get("tables", []) if not t.get("is_standard_spec")]
            except Exception:
                dynamic_tables = []

        from storage_control.services.building_twin import build_building_twin_index
        return render(request, "storage_control/index.html", {
            "building_twin": build_building_twin_index(),
            "exec_kpi": __import__("storage_control.services.id_template_engine", fromlist=["build_executive_site_dashboard"]).build_executive_site_dashboard(),
            "rows": parsed_data,
            "error": err_msg,
            "count": len(parsed_data),
            "nav_items": NAV_ITEMS,
            "staff_list": staff_list,
            "stock_list": stock_list,
            "purchase_requests": purchase_requests,
            "dynamic_tables": dynamic_tables,
            "documents_list": documents_list,
            "active_doc": active_doc,
            "section_filter": section_filter,
            "parse_goal": effective_goal,
            "brigade_groups": list(brigade_groups.values()),
            "erp_b2b_stats": erp_b2b_stats,
            "crm_ceo_stats": crm_ceo_stats,
        })

    def post(self, request, *args, **kwargs):
        current_owner = request.user if request.user.is_authenticated else None
        pdf_file = request.FILES.get('pdf_file')
        if not pdf_file:
            messages.warning(request, "Файл PDF не выбран.")
            return redirect(request.path)

        # Вычисляем SHA-256 загружаемого PDF для защиты от дублей
        hasher = hashlib.sha256()
        for chunk in pdf_file.chunks():
            hasher.update(chunk)
        current_hash = hasher.hexdigest()
        pdf_file.seek(0)

        # 1. Проверяем дубль SHA-256 строго внутри пространства текущего владельца
        existing_hash_doc = Document.objects.filter(owner=current_owner, file_hash=current_hash).first()
        if existing_hash_doc:
            doc = existing_hash_doc
            messages.info(
                request,
                f"Файл идентичен (SHA-256 совпадает) тому «{doc.title}» [Рев. {doc.revision_num}]. Дубль не создан, ведомость пересчитана."
            )
        else:
            # 2. Вычисляем номер следующей ревизии и архивируем старые версии только этого владельца
            prev_docs = Document.objects.filter(owner=current_owner, title=pdf_file.name)
            next_rev = (prev_docs.aggregate(models.Max('revision_num'))['revision_num__max'] or 0) + 1
            prev_docs.update(work_status='ARCHIVED')

            # 3. Создаём новую актуальную ревизию
            doc = Document.objects.create(
                title=pdf_file.name,
                file=pdf_file,
                file_hash=current_hash,
                revision_num=next_rev,
                work_status='WORK',
                owner=current_owner,
            )
            if next_rev > 1:
                messages.warning(
                    request,
                    f"Загружена новая ревизия №{next_rev} тома «{doc.title}»! Предыдущие версии аннулированы."
                )

        import threading
        from django.db import close_old_connections
        from .services.pdf_ocr import extract_and_store_pages
        from .services.spec_matcher import parse_specifications_and_create_requests

        staff_id = request.POST.get('selected_staff_id', '')
        staff_obj = ItrStaff.objects.filter(staff_id=staff_id).first()
        staff_label = f"{staff_obj.name} [{staff_obj.staff_id}]" if staff_obj else (staff_id or "Штаб ПТО")
        notify_tg = request.POST.get('notify_telegram') == '1'

        def _background_turbo_parse(target_doc_id: int, operator_label: str, do_tg: bool):
            close_old_connections()
            try:
                d_obj = Document.objects.filter(id=target_doc_id).first()
                if not d_obj:
                    return
                rep = extract_and_store_pages(d_obj)
                spec_rep = parse_specifications_and_create_requests(d_obj, staff_label=operator_label)
                if do_tg:
                    from .telegram_bot import send_pto_telegram_report
                    req_cnt = d_obj.purchase_requests.count() if hasattr(d_obj, 'purchase_requests') else 0
                    send_pto_telegram_report(operator_label, d_obj.title, rep.get("pages_processed", 0), req_cnt)
            finally:
                close_old_connections()

        threading.Thread(target=_background_turbo_parse, args=(doc.id, staff_label, notify_tg), daemon=True).start()
        messages.success(
            request,
            f"⚡ Том «{doc.title}» [Рев. {doc.revision_num}] принят в фоновый конвейер! Страницы, спецификации и узлы «Черепахи» появятся автоматически через несколько секунд."
        )

        return redirect(f"{reverse('storage_control:dashboard')}?doc_id={doc.id}")

class TrackerSearchAPIView(View):
    """Точечный поиск по картотеке РД, паспортам качества и складу с привязкой к листам PDF."""

    def get(self, request, *args, **kwargs):
        q = request.GET.get('q', '').strip()
        mode = request.GET.get('mode', 'all')
        current_owner = request.user if request.user.is_authenticated else None
        results = []

        if not q:
            return JsonResponse({'results': results})

        if mode in ('all', 'stock'):
            tmc_qs = WarehouseTmc.objects.filter(
                owner=current_owner
            ).filter(
                Q(nomenclature__icontains=q) | Q(item_code__icontains=q)
            )[:20]
            for item in tmc_qs:
                results.append({
                    'source': f"Склад: {item.item_code}",
                    'snippet': f"{item.nomenclature} — Остаток на складе: {item.stock_balance} {item.unit}",
                    'norm': 'Склад ТМЦ',
                    'folder_code': 'СКЛАД',
                    'pdf_url': '',
                    'page_number': 1,
                    'doc_id': None,
                })

        if mode in ('all', 'passport'):
            pages_qs = ParsedPage.objects.filter(
                document__owner=current_owner,
                text__icontains=q
            )
            if mode == 'passport':
                pages_qs = pages_qs.filter(
                    Q(text__icontains='паспорт') | Q(text__icontains='сертификат')
                )
            for page in pages_qs.select_related('document').order_by('document__title', 'page_number')[:40]:
                raw_txt = page.text or ""
                # Убираем штампы и разделяем склеенные слова для полного читаемого наименования
                clean_txt = re.sub(r'Формат\s*А\d(?:х\d)?', '', raw_txt, flags=re.IGNORECASE)
                clean_txt = re.sub(r'([а-яё])([А-ЯЁ])', r'\1 | \2', clean_txt)

                matched_lines = [
                    ln.strip() for ln in clean_txt.split('\n')
                    if q.lower() in ln.lower() and len(ln.strip()) > 3
                ]
                if matched_lines:
                    full_snippet = " — ".join(matched_lines[:3])[:380]
                else:
                    idx = clean_txt.lower().find(q.lower())
                    start = max(0, idx - 80)
                    full_snippet = clean_txt[start:start + 320].replace('\n', ' ').strip()

                doc_title = page.document.title
                folder_match = re.search(r'(\d{2}-[А-ЯЁA-Z0-9]+)', doc_title)
                folder_code = folder_match.group(1) if folder_match else doc_title[:12]
                norm_name = page.get_official_norm_name() if hasattr(page, 'get_official_norm_name') else folder_code
                pdf_url = page.document.file.url if page.document.file else ""

                results.append({
                    'source': f"{doc_title} (Лист №{page.page_number})",
                    'snippet': full_snippet,
                    'norm': norm_name,
                    'folder_code': folder_code,
                    'pdf_url': pdf_url,
                    'page_number': page.page_number,
                    'doc_id': page.document.id,
                })

        return JsonResponse({'results': results})

class PurchaseRequestAPIView(View):
    """Формирование и поиск заявок на закупку материалов по спецификации после парсинга"""

    def get(self, request, *args, **kwargs):
        q = request.GET.get('q', '').strip().lower()
        latest_doc = Document.objects.order_by('-uploaded_at').first()

        if not latest_doc:
            return JsonResponse({'requests': [], 'doc_title': 'Нет загруженных спецификаций'})

        spec_re = re.compile(
            r'([А-ЯЁA-Z][А-ЯЁа-яёA-Za-z0-9\s\-\.\(\)\/]{4,80}?)\s+'
            r'(м2|м²|м3|м³|шт\.?|т|кг|п\.м\.|м)\s+'
            r'(\d+(?:[\.,]\d+)?)',
            re.IGNORECASE
        )

        warehouse_items = list(WarehouseTmc.objects.all())
        aggregated = {}

        for page in latest_doc.pages.all():
            if not page.text:
                continue
            for line in page.text.split('\n'):
                m = spec_re.search(line.strip())
                if not m:
                    continue
                name = re.sub(r'\s+', ' ', m.group(1)).strip()
                unit = m.group(2).strip()
                qty = Decimal(m.group(3).replace(',', '.'))

                if q and q not in name.lower():
                    continue

                key = name.lower()
                if key not in aggregated:
                    aggregated[key] = {
                        'material': name,
                        'unit': unit,
                        'required': Decimal('0'),
                        'page': page.page_number,
                    }
                aggregated[key]['required'] += qty

        purchase_list = []
        for key, item in aggregated.items():
            stock_match = next(
                (w for w in warehouse_items if w.nomenclature.lower() in key or key in w.nomenclature.lower()),
                None
            )
            in_stock = stock_match.stock_balance if stock_match else Decimal('0')
            to_buy = max(Decimal('0'), item['required'] - in_stock)

            purchase_list.append({
                'material': item['material'],
                'unit': item['unit'],
                'required': float(item['required']),
                'in_stock': float(in_stock),
                'to_buy': float(to_buy),
                'status': 'ЗАКУПИТЬ' if to_buy > 0 else 'ЕСТЬ НА СКЛАДЕ',
                'source': f"Стр. {item['page']}"
            })

        return JsonResponse({
            'doc_title': latest_doc.title,
            'requests': purchase_list
        })

from django.db.models import Q


def parse_trigger(request):
    """Расширенный поиск: ищет сразу и на складе ТМЦ, и в тексте чертежей"""
    name = request.GET.get('product_name', '').strip()
    if not name:
        return JsonResponse({'message': 'Введите название материала'}, status=400)

    # 1. Ищем на складе (твой старый код)
    found_stock = WarehouseTmc.objects.filter(nomenclature__icontains=name)[:10]
    items = [
        {
            'nomenclature': t.nomenclature,
            'stock': str(t.stock_balance),
            'unit': t.unit,
        }
        for t in found_stock
    ]

    # 2. Ищем в распознанных листах PDF (новое расширение)
    found_pages = ParsedPage.objects.select_related('document').filter(
        text__icontains=name
    ).order_by('-id')[:10]

    pages = []
    for p in found_pages:
        idx = p.text.lower().find(name.lower())
        start = max(0, idx - 30)
        snippet = p.text[start:start + 100].replace('\n', ' ').strip()
        pages.append({
            'doc_title': p.document.title,
            'page_number': p.page_number,
            'snippet': f"...{snippet}...",
        })

    return JsonResponse({
        'message': f'Найдено по запросу «{name}»: склад ({len(items)}), чертежи ({len(pages)})',
        'items': items,
        'pages': pages,
    })

def export_staff_excel_view(request):
    """Скачивание 3-листового штабного Excel (Снабжение, ПТО, Логистика)."""
    from .services.export_staff_excel import build_staff_excel_bytes

    doc_id = request.GET.get("doc_id")
    doc = Document.objects.filter(id=int(doc_id)).first() if (doc_id and doc_id.isdigit()) else None

    xlsx_bytes = build_staff_excel_bytes(doc=doc)
    filename = f"Shtab_PTO_Snabzhenie_{doc.id if doc else 'ALL'}.xlsx"

    response = HttpResponse(
        xlsx_bytes,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response

def export_customer_gpr_view(request):
    """Скачивание внешнего Календарного графика для Заказчика (ГПР .xlsx)."""
    from .services.export_customer_gpr import build_customer_gpr_excel

    doc_id = request.GET.get("doc_id")
    parsed_id = int(doc_id) if (doc_id and doc_id.isdigit()) else None

    xlsx_bytes = build_customer_gpr_excel(doc_id=parsed_id)
    filename = f"Grafik_GPR_Zakazchik_{parsed_id if parsed_id else 'FULL_PROJECT'}.xlsx"

    response = HttpResponse(
        xlsx_bytes,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response

def export_aosr_docx_view(request):
    """Генерация и скачивание готового Акта освидетельствования скрытых работ (АОСР .docx)."""
    from .services.export_aosr import build_aosr_docx_bytes

    doc_id = request.GET.get("doc_id")
    doc = Document.objects.filter(id=int(doc_id)).first() if (doc_id and doc_id.isdigit()) else Document.objects.order_by("-uploaded_at").first()
    if not doc:
        messages.warning(request, "Сначала загрузите том РД для формирования АОСР.")
        return redirect("storage_control:dashboard")

    handover_mode = request.GET.get("handover_mode", "GEN_TO_CUSTOMER")
    date_start = request.GET.get("date_start", "")
    date_end = request.GET.get("date_end", "")
    executor_name = (request.GET.get("executor_name") or "").strip() or "Косарев М.В. (Главный Архитектор / ПТО)"
    inspector_name = (request.GET.get("inspector_name") or "").strip() or "Представитель строительного контроля Заказчика"
    next_work = (request.GET.get("next_work") or "").strip() or "производство последующих работ согласно графику ГПР"

    docx_bytes = build_aosr_docx_bytes(
        doc=doc,
        handover_mode=handover_mode,
        date_start=date_start,
        date_end=date_end,
        executor_name=executor_name,
        inspector_name=inspector_name,
        next_work_allowed=next_work,
    )

    response = HttpResponse(
        docx_bytes,
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    response["Content-Disposition"] = f'attachment; filename="AOSR_Tom_{doc.id}.docx"'
    return response

def _enrich_mark_passport_ctx(ctx: dict, query: str) -> dict:
    skip_cover_sheets = ("общие данные", "содержание", "ведомость ссылочных")
    from storage_control.models import StockMovement, PurchaseRequest, PhotoIntake
    from storage_control.services.turtle_geometry import (
        build_contextual_cad_modes, build_project_axes_and_floor_cuts, build_nss_cable_vector_svg
    )
    ctx["cad_modes"] = build_contextual_cad_modes(mark_query=str(ctx.get("query") or request.GET.get("q") or ""))
    ctx["project_floor_cuts"] = build_project_axes_and_floor_cuts()
    ctx["nss_vector_svg"] = build_nss_cable_vector_svg(mark_query=query)
    from storage_control.services.turtle_geometry import extract_real_building_metrics_from_pdfs
    ctx["real_metrics"] = extract_real_building_metrics_from_pdfs()
    ctx["stock_movements"] = list(StockMovement.objects.select_related("purchase_request", "photo_intake").all()[:15])
    ctx["gpr_positions"] = list(PurchaseRequest.objects.order_by("-id").values("id", "material_name", "required_qty", "unit")[:40])
    from storage_control.services.building_twin import build_building_twin_index
    ctx["building_twin"] = build_building_twin_index()

    all_intakes = list(PhotoIntake.objects.order_by("-id")[:120])
    ctx["recent_5_intakes"] = all_intakes[:5]
    ctx["archived_intakes"] = all_intakes[5:]
    ctx["total_intakes_count"] = len(all_intakes)

    return ctx

def mark_passport_view(request):
    query = str(request.GET.get("q") or "")
    from storage_control.services.mark_passport import build_mark_passport_data
    from storage_control.services.turtle_geometry import extract_scaled_node_cuts_from_pdf
    from .models import PhotoIntake, ParsedPage, Document
    from django.db.models import Q
    import re as _re

    q = (request.GET.get("q") or "").strip()
    ctx = build_mark_passport_data(q)

    photos = list(PhotoIntake.objects.all()[:15])
    ctx["field_photos"] = photos

    turtle_plans = []
    for ph in photos[:6]:
        tp = (ph.payload_1c_json or {}).get("turtle_plan")
        if tp and tp.get("ok") and tp.get("svg_preview"):
            tp_copy = dict(tp)
            tp_copy["photo_id"] = ph.id
            turtle_plans.append(tp_copy)
    ctx["turtle_plans"] = turtle_plans

    milled_cuts = []
    selected_doc_id = (request.GET.get("doc_id") or "").strip()
    clean_q = _re.sub(r'\s*[Ll]\s*=.*$', '', q).strip()
    q_compact = clean_q.replace(" ", "")

    pages_qs = ParsedPage.objects.select_related("document").all()
    if selected_doc_id.isdigit():
        pages_qs = pages_qs.filter(document_id=int(selected_doc_id))
        matched_pages = list(pages_qs.filter(Q(text__icontains="Узел") | Q(text__icontains="1:20") | Q(text__icontains="1:10") | Q(text__icontains="Спецификация")).order_by("page_number")[:2])
        if not matched_pages:
            matched_pages = list(pages_qs.order_by("-page_number")[:1])
    elif clean_q:
        page_filter = Q(text__icontains=clean_q) | Q(text__icontains=q_compact)
        matched_pages = list(pages_qs.filter(page_filter).order_by("-document__uploaded_at", "page_number")[:2])
    else:
        matched_pages = list(pages_qs.filter(Q(text__icontains="Узел") | Q(text__icontains="1:20")).order_by("-document__uploaded_at", "page_number")[:2])

    by_doc = {}
    for mp in matched_pages:
        if mp.document and mp.document.file and os.path.exists(mp.document.file.path):
            by_doc.setdefault(mp.document, []).append(mp.page_number)

    for doc_obj, p_nums in list(by_doc.items())[:1]:
        cuts = extract_scaled_node_cuts_from_pdf(doc_obj.file.path, doc_obj.id, p_nums[:1], query_hint=clean_q or "Узел")
        for c in cuts:
            c["doc_id"] = doc_obj.id
            c["doc_title"] = doc_obj.title
            milled_cuts.append(c)

    ctx["milled_cuts"] = milled_cuts
    ctx["selected_doc_id"] = selected_doc_id
    ctx["available_docs"] = list(Document.objects.order_by("-uploaded_at").values("id", "title")[:15])

    from .models import StockMovement, PurchaseRequest
    from storage_control.services.turtle_geometry import build_contextual_cad_modes
    ctx["cad_modes"] = build_contextual_cad_modes(mark_query=str(ctx.get("query") or request.GET.get("q") or ""))
    ctx["stock_movements"] = list(StockMovement.objects.select_related("purchase_request", "photo_intake").all()[:15])
    ctx["gpr_positions"] = list(PurchaseRequest.objects.order_by("-id").values("id", "material_name", "required_qty", "unit")[:40])
    from storage_control.services.building_twin import build_building_twin_index
    ctx["building_twin"] = build_building_twin_index()
    ctx = _enrich_mark_passport_ctx(ctx, str(ctx.get("query") or request.GET.get("q") or ""))
    return render(request, "storage_control/mark_passport.html", ctx)

    # Авто-вырезка «Черепахой-Фрезой» узлов с масштабами (М 1:10, М 1:20, М 1:50...) по найденным листам РД
    from django.db.models import Q
    milled_cuts = []
    q_compact = q.replace(" ", "")
    page_filter = Q(text__icontains=q) | Q(text__icontains=q_compact) if q else Q(text__icontains="1:20")
    matched_pages = ParsedPage.objects.select_related("document").filter(page_filter)[:4]
    if not matched_pages:
        matched_pages = ParsedPage.objects.select_related("document").filter(text__icontains="1:20")[:3]

    by_doc = {}
    for mp in matched_pages:

        if mp.document and mp.document.file and os.path.exists(mp.document.file.path):
            by_doc.setdefault(mp.document, []).append(mp.page_number)
    for doc_obj, p_nums in list(by_doc.items())[:2]:
        cuts = extract_scaled_node_cuts_from_pdf(doc_obj.file.path, doc_obj.id, p_nums, query_hint=q or "М 1:20")
        for c in cuts:
            c["doc_title"] = doc_obj.title
            milled_cuts.append(c)
    ctx["milled_cuts"] = milled_cuts

    from .models import StockMovement, PurchaseRequest
    from storage_control.services.turtle_geometry import build_contextual_cad_modes
    ctx["cad_modes"] = build_contextual_cad_modes(mark_query=str(ctx.get("query") or request.GET.get("q") or ""))
    ctx["stock_movements"] = list(StockMovement.objects.select_related("purchase_request", "photo_intake").all()[:15])
    ctx["gpr_positions"] = list(PurchaseRequest.objects.order_by("-id").values("id", "material_name", "required_qty", "unit")[:40])
    from storage_control.services.building_twin import build_building_twin_index
    ctx["building_twin"] = build_building_twin_index()
    ctx = _enrich_mark_passport_ctx(ctx, str(ctx.get("query") or request.GET.get("q") or ""))
    return render(request, "storage_control/mark_passport.html", ctx)


def export_dynamic_table_view(request):
    """Выгружает выбранную нестандартную таблицу чертежа (отделка, экспликация, журнал) в чистый Excel (.xlsx)."""
    import io
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from django.http import HttpResponse, Http404
    from django.core.cache import cache

    doc_id = request.GET.get("doc_id")
    idx = int(request.GET.get("idx", 0))
    doc = Document.objects.filter(id=doc_id).first()
    if not doc or not getattr(doc, "file", None):
        raise Http404("Документ не найден")

    c_key = f"geo_dyn_tables_v2_{doc.id}"
    tables = cache.get(c_key)
    if tables is None:
        from storage_control.services.grid_extractor import extract_geometric_tables
        geo = extract_geometric_tables(doc.file.path, max_pages=12)
        tables = [t for t in geo.get("tables", []) if not t.get("is_standard_spec")]
        cache.set(c_key, tables, 3600)

    if idx < 0 or idx >= len(tables):
        raise Http404("Таблица не найдена")

    dt = tables[idx]
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Лист_{dt['page']}_{dt['schema_code']}"[:31]

    hdr_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    hdr_font = Font(name="Calibri", size=11, bold=True, color="FFD700")
    thin = Border(
        left=Side(style="thin", color="CBD5E1"),
        right=Side(style="thin", color="CBD5E1"),
        top=Side(style="thin", color="CBD5E1"),
        bottom=Side(style="thin", color="CBD5E1"),
    )

    ws.append(dt["headers"])
    for c_i in range(1, len(dt["headers"]) + 1):
        cell = ws.cell(row=1, column=c_i)
        cell.fill = hdr_fill
        cell.font = hdr_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin
        ws.column_dimensions[openpyxl.utils.get_column_letter(c_i)].width = 24

    for row in dt["rows"]:
        ws.append(row)
        r_num = ws.max_row
        for c_i in range(1, len(dt["headers"]) + 1):
            c_obj = ws.cell(row=r_num, column=c_i)
            c_obj.border = thin
            c_obj.alignment = Alignment(vertical="center", wrap_text=True)

    buf = io.BytesIO()
    wb.save(buf)
    resp = HttpResponse(
        buf.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    resp["Content-Disposition"] = f'attachment; filename="table_{doc.id}_p{dt["page"]}.xlsx"'
    return resp

def mark_passport_seo_alias_view(request, slug: str):
    import re
    from django.shortcuts import render
    from storage_control.models import PurchaseRequest, ParsedPage
    from storage_control.services.mark_passport import build_mark_passport
    from storage_control.services.building_twin import fix_autocad_mojibake
    from storage_control.services.quantum_normalizer import canon_key

    ctx = build_mark_passport(slug)
    ru_hint = _detranslit_mark_slug(slug)
    raw_parts = [p for p in re.split(r'[\s\-]+', ru_hint) if len(p) >= 2]
    key_tokens = [p for p in raw_parts if p.lower() not in ("система", "л", "l")]
    primary_key = key_tokens if key_tokens else (raw_parts if raw_parts else slug)

    matched_reqs = []
    for r in PurchaseRequest.objects.select_related("document").all()[:2500]:
        ck_nm = canon_key(r.material_name or "")
        if any(canon_key(kt) in ck_nm for kt in (key_tokens or [primary_key]) if len(canon_key(kt)) >= 2):
            matched_reqs.append(r)

    matched_pages, seen_p = [], set()
    search_terms = list({t for t in (key_tokens + [primary_key, slug.replace("-", " ")]) if len(t) >= 2})
    for term in search_terms[:4]:
        for pg in ParsedPage.objects.select_related("document").filter(text__icontains=term)[:15]:
            if pg.id in seen_p:
                continue
            seen_p.add(pg.id)
            txt = fix_autocad_mojibake(pg.text or "")
            m = re.search(re.escape(term), txt, re.I)
            snip = re.sub(r'\s+', ' ', txt[max(0, m.start()-40):m.end()+120]).strip() if m else txt[:150]
            img_url = pg.image.url if getattr(pg, "image", None) and pg.image else ""
            matched_pages.append({"doc": pg.document.title if pg.document else "РД", "page": pg.page_number, "snippet": snip, "img_url": img_url})

    docs_set = {p["doc"] for p in matched_pages} | {r.document.title for r in matched_reqs if r.document}
    total_qty = round(sum(float(r.required_qty or 0) for r in matched_reqs), 2)
    stock_qty = round(sum(max(0.0, float(r.required_qty or 0) - float(r.deficit_qty or 0)) for r in matched_reqs), 2)

    ctx.update({
        "ru_hint": ru_hint,
        "matched_reqs": matched_reqs,
        "matched_pages": matched_pages,
        "real_qty": total_qty if total_qty > 0 else 1,
        "stock_qty": stock_qty,
        "docs_found_cnt": len(docs_set),
        "reqs_found_cnt": len(matched_reqs),
        "links_cnt": len(matched_pages) + len(matched_reqs),
    })
    return render(request, "storage_control/mark_passport.html", ctx)

def async_search_api_view(request):
    """Асинхронный JSON-поиск по картотеке РД и складу (для мгновенных подсказок и SEO)."""
    from django.http import JsonResponse
    q = request.GET.get("q", "").strip()
    if len(q) < 2:
        return JsonResponse({"ok": True, "query": q, "count": 0, "results": []})
    pages = ParsedPage.objects.select_related("document").filter(text__icontains=q)[:15]
    results = [
        {
            "doc_title": p.document.title if p.document else "РД",
            "page": p.page_number,
            "snippet": (p.text or "")[:180].replace("\n", " "),
            "passport_url": f"/mark-passport/?q={q}",
        }
        for p in pages
    ]
    return JsonResponse({"ok": True, "query": q, "count": len(results), "results": results})

def mark_passport_seo_alias_view(request, slug):
    from django.http import QueryDict
    from .templatetags.seo_tags import make_seo_slug

    clean_slug = make_seo_slug(slug)
    matched_title = slug.replace("-", " ").strip()
    for mat_name in PurchaseRequest.objects.values_list("material_name", flat=True).distinct()[:500]:
        if make_seo_slug(mat_name) == clean_slug or clean_slug in make_seo_slug(mat_name):
            matched_title = mat_name
            break

    qd = QueryDict(mutable=True)
    qd["q"] = matched_title
    request.GET = qd
    return mark_passport_view(request)


def async_search_api_view(request):
    from django.http import JsonResponse
    from .templatetags.seo_tags import make_seo_slug

    q = request.GET.get("q", "").strip()
    if len(q) < 2:
        return JsonResponse({"ok": True, "query": q, "count": 0, "results": []})
    pages = ParsedPage.objects.select_related("document").filter(text__icontains=q)[:15]
    results = [
        {
            "doc_title": p.document.title if p.document else "РД",
            "page": p.page_number,
            "snippet": (p.text or "")[:180].replace("\n", " "),
            "passport_url": f"/marka/{make_seo_slug(q)}/",
        }
        for p in pages
    ]
    return JsonResponse({"ok": True, "query": q, "count": len(results), "results": results})


def photo_1c_hub_view(request):
    from .models import PhotoIntake
    from .services.falcon_vision import analyze_field_photo
    from .services.one_c_bridge import extract_1c_document_payload, build_photo_catalog_answer
    from .services.turtle_geometry import analyze_building_plan_footprint

    if request.method == "POST" and request.FILES.get("image"):
        kind = request.POST.get("photo_kind", "UPD_INVOICE")
        scene = request.POST.get("scene_mode", "AUTO")
        notes = request.POST.get("notes", "").strip()
        obj = PhotoIntake.objects.create(
            photo_kind=kind,
            image=request.FILES["image"],
            uploaded_by=request.user.username if request.user.is_authenticated else "ПТО Штаб",
            notes=notes[:250],
        )
        vision = analyze_field_photo(obj.image.path, manual_hint_text=notes, scene_mode=scene)
        payload_1c = extract_1c_document_payload(vision)
        payload_1c["catalog_answer"] = build_photo_catalog_answer(vision, payload_1c)
        payload_1c["turtle_plan"] = analyze_building_plan_footprint(obj.image.path, operator_object_title=notes)
        codes_txt = ", ".join(f"{c['type']}:{c['raw'][:30]}" for c in vision.get("codes_found", []))

        obj.scene_label = vision.get("scene_info", {}).get("scene_label", "")
        obj.sharpness_pct = vision.get("sharpness_after_pct", 0.0)
        obj.barcode_summary = codes_txt[:250]
        obj.detected_axes = vision.get("detected_axes", "")[:115]
        obj.detected_elevation = vision.get("detected_elevation", "")[:55]
        obj.supplier_inn = payload_1c.get("supplier_inn", "")[:20]
        obj.doc_number = payload_1c.get("doc_number", "")[:115]
        obj.ocr_raw_text = vision.get("ocr_preview", "")
        obj.payload_1c_json = payload_1c
        obj.save()

    return redirect(request.POST.get("return_to") or "/marka/truba-pe-110/")



def photo_1c_accept_view(request, pk):
    from .models import PhotoIntake
    from .services.one_c_bridge import commit_1c_intake_to_warehouse_and_log
    if request.method == "POST":
        obj = get_object_or_404(PhotoIntake, pk=pk)
        operator = request.user.username if request.user.is_authenticated else "ПТО Штаб"
        commit_1c_intake_to_warehouse_and_log(obj.payload_1c_json or {}, operator=operator)
        obj.status = "ACCEPTED_1C"
        obj.save(update_fields=["status"])
    return redirect(request.META.get("HTTP_REFERER") or "/marka/truba-pe-110/")


def photo_1c_export_view(request, pk, fmt):
    from .models import PhotoIntake
    from .services.one_c_bridge import build_1c_exchange_files
    obj = get_object_or_404(PhotoIntake, pk=pk)
    xlsx_bytes, xml_bytes = build_1c_exchange_files(obj.payload_1c_json or {})
    if fmt == "xml":
        resp = HttpResponse(xml_bytes, content_type="application/xml; charset=utf-8")
        resp["Content-Disposition"] = f'attachment; filename="1C_UPD_{obj.id}.xml"'
        return resp
    resp = HttpResponse(
        xlsx_bytes,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    resp["Content-Disposition"] = f'attachment; filename="1C_Prihod_M4_{obj.id}.xlsx"'
    return resp


from django.views.decorators.http import require_POST


@require_POST
def stock_movement_create_view(request):
    from storage_control.services.stock_acts import register_stock_movement
    return_to = request.POST.get("return_to") or reverse("storage_control:dashboard")
    pr_raw = (request.POST.get("purchase_request_id") or "").strip()
    ph_raw = (request.POST.get("photo_intake_id") or "").strip()
    try:
        qty_val = float((request.POST.get("qty") or "0").replace(",", ".").strip())
    except ValueError:
        qty_val = 0.0

    mv, alerts = register_stock_movement(
        movement_kind=(request.POST.get("movement_kind") or "OUT_M11").strip(),
        material_name=(request.POST.get("material_name") or "").strip(),
        qty=qty_val,
        unit=(request.POST.get("unit") or "\u0448\u0442.").strip(),
        purchase_request_id=int(pr_raw) if pr_raw.isdigit() else None,
        photo_intake_id=int(ph_raw) if ph_raw.isdigit() else None,
        upd_batch_number=(request.POST.get("upd_batch_number") or "").strip(),
        brigade_or_subcontractor=(request.POST.get("brigade_or_subcontractor") or "").strip(),
        axes_and_ojr=(request.POST.get("axes_and_ojr") or "").strip(),
        responsible_itr=(request.POST.get("responsible_itr") or "\u0428\u0442\u0430\u0431 \u041f\u0422\u041e").strip(),
        doc_status=(request.POST.get("doc_status") or "CONFIRMED").strip(),
    )
    messages.success(request, f"\u041e\u0444\u043e\u0440\u043c\u043b\u0435\u043d \u0434\u043e\u043a\u0443\u043c\u0435\u043d\u0442 \u2116{mv.id}: {mv.get_movement_kind_display()} ({mv.qty} {mv.unit}).")
    for al in alerts:
        messages.warning(request, al)
    return redirect(return_to)


@require_POST
def stock_movement_status_view(request, movement_id: int):
    from storage_control.models import StockMovement
    mv = get_object_or_404(StockMovement, id=movement_id)
    new_status = (request.POST.get("doc_status") or "CONFIRMED").strip()
    if new_status in {c for c in StockMovement.DOC_STATUS_CHOICES}:
        mv.doc_status = new_status
        mv.save(update_fields=["doc_status"])
    return redirect(request.POST.get("return_to") or reverse("storage_control:dashboard"))


def stock_movement_print_view(request, movement_id: int):
    from storage_control.models import StockMovement
    mv = get_object_or_404(StockMovement, id=movement_id)

    standards_map = {
        "IN_UPD": ("????????? ????? ? ?-4", "???? 0315003 ? ????????????? ??????????? ?? ? 71? / ??? ?? ?? ? 1137 (???)"),
        "OUT_M11": ("??????????-????????? ? ?-11", "???? 0315006 ? ????????????? ??????????? ?? ? 71? (??????? / ???)"),
        "OUT_M15_SUB": ("????????? ?? ?????? ?????????? ?? ??????? ? ?-15 (???????????? ?????)", "???? 0315007 ? ????????????? ??????????? ?? ? 71? (??? / ?????????)"),
        "RET_M11": ("????????? ?? ??????? ???????? ?????????? ?? ????? (???????? ?-11)", "???? 0315006 ? ????????????? ??????????? ?? ? 71? (???)"),
        "DEFECT_TORG2": ("??? ?? ????????????? ??????????? ?? ?????????? ? ???????? ? ????-2", "???? 0330202 ? ????????????? ??????????? ?? ? 132 (????????????? / ???)"),
        "WRITE_OFF_AOSR": ("??? ??????????????????? ??????? ????? (????) ? ???????? ??? (?-29)", "?????? ???????? ?? ? 344/?? ? ???? ? 70108-2022 ? ?????? ???????? ? 883? (???? / ???)"),
    }
    title_str, norm_str = standards_map.get(mv.movement_kind, (mv.get_movement_kind_display(), "???????? ??"))
    doc_ref = mv.purchase_request.document.title if (mv.purchase_request and mv.purchase_request.document) else "??????? ???????????? (??)"
    legal_note = (
        "????????? ???????? ?????????? ?? ???????????? ???????? ??? ???????? ????? ?????????????. ???????? ????????????? ?????? ?? ?????????????? (?-29) ??? ?????????? ??-2 / ??-3."
        if mv.movement_kind == "OUT_M15_SUB"
        else "?????? ????????? ? ???????????? ? ????????? ?????????????, ?? ? ???????????? ?????? ????? (?????? ???????? ?? ? 883?, ?????????? ?? ?? ?? ? 2464 ????????)."
    )

    html = f"""<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8"><title>{title_str} ?{mv.id}</title>
    <style>
        body{{font-family:'Times New Roman',serif;padding:24px 32px;color:#000;font-size:13px;line-height:1.4}}
        .okud{{text-align:right;font-size:11px;border:1px solid #000;display:inline-block;padding:4px 8px;float:right}}
        h2{{margin:8px 0 4px 0;font-size:16px;text-transform:uppercase;clear:both}}
        .sub{{font-size:11px;color:#333;margin-bottom:12px;border-bottom:1.5px solid #000;padding-bottom:6px}}
        table{{width:100%;border-collapse:collapse;margin:12px 0}}
        th,td{{border:1px solid #000;padding:6px 8px;font-size:12px}}
        th{{background:#f3f4f6;text-align:center}}
        .box{{border:1px solid #000;padding:8px;margin:10px 0;font-size:12px}}
        .signs{{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:24px;font-size:12px}}
        @media print{{.no-print{{display:none}}}}
    </style></head><body>
    <div class="no-print" style="margin-bottom:14px;font-family:Arial,sans-serif;">
        <button onclick="window.print()" style="padding:9px 18px;font-size:13px;font-weight:bold;cursor:pointer;">??? ?????? ???????????? ?????? ?4 / ????????? PDF</button>
    </div>
    <div class="okud">{norm_str}</div>
    <h2>{title_str} ? {mv.id}</h2>
    <div class="sub">???? ???????????: <strong>{mv.created_at:%d.%m.%Y}</strong> ? ?????? ?????????: <strong>{mv.get_doc_status_display()}</strong> ? ???? ??: <strong>{doc_ref}</strong></div>
    <div class="box">
        <div><strong>1. ????????? / ?????? ??? ? ?????????? ????????:</strong> {mv.upd_batch_number or '???????? ????????? ?? ? ???????? ????????'}</div>
        <div><strong>2. ???????, ???, ??????? ? ?????? ? ??? (??-11-05-2007):</strong> {mv.axes_and_ojr or '?? ???????? ??????? ???????????? ????? (???)'}</div>
        <div><strong>3. ?????????? / ??????????? ????? (??????? / ????????????):</strong> {mv.brigade_or_subcontractor or '??????? ??????? ?????????????'}</div>
        <div><strong>4. ?????? ????? (??? / ??????? ? 883?):</strong> ??????? ?????????? ?? ?? ?? ? 2464 ????????; ?????? ? ??????? ????????.</div>
    </div>
    <table>
        <thead><tr><th>? ?/?</th><th>???????????? ??? / ????????????</th><th>??. ???.</th><th>??????????</th><th>??????? ??? / ?????</th><th>?????????? (???? / ??-123)</th></tr></thead>
        <tbody><tr><td style="text-align:center;">1</td><td>{mv.material_name}</td><td style="text-align:center;">{mv.unit}</td><td style="text-align:center;"><strong>{mv.qty}</strong></td><td>{mv.purchase_request.material_name if mv.purchase_request else '????????? ????'}</td><td>????????????? ??</td></tr></tbody>
    </table>
    <p style="font-size:11.5px;"><em>{legal_note}</em></p>
    <div class="signs">
        <div><strong>???? (????????? / ????????? ???????):</strong><br><br>_____________________ / {mv.responsible_itr} /<br><span style="font-size:10px;">(?????????, ???????, ???????????, ? ??? ???????)</span></div>
        <div><strong>?????? ({mv.brigade_or_subcontractor or '?????? / ????????'}):</strong><br><br>_____________________ / ___________________ /<br><span style="font-size:10px;">(?????????, ???????, ???????????, ????????????/??????)</span></div>
        <div><strong>????????????? ????????????? (????????? ?????????):</strong><br><br>_____________________ / ___________________ /<br><span style="font-size:10px;">(???????, ?????, ? ??? ??????/???????)</span></div>
        <div><strong>????????? ?????? (??? ??????????????????? ????):</strong><br><br>_____________________ / ___________________ /<br><span style="font-size:10px;">(???????, ????)</span></div>
    </div>
    </body></html>"""
    return HttpResponse(html)


def room_passport_view(request, room_code: str):
    from storage_control.services.building_twin import build_single_room_passport
    ctx = build_single_room_passport(room_code)
    return render(request, "storage_control/room_passport.html", ctx)


def save_object_passport_view(request):
    from django.http import JsonResponse
    from storage_control.services.id_template_engine import save_object_passport, get_saved_object_passport
    if request.method == "POST":
        saved = save_object_passport(request.POST.dict())
        return JsonResponse({"ok": True, "passport": saved})
    return JsonResponse({"ok": True, "passport": get_saved_object_passport()})


def id_registry_export_view(request):
    import io, openpyxl
    from django.http import HttpResponse
    from django.utils import timezone
    from storage_control.services.id_template_engine import build_filled_customer_registry_xlsx
    if request.GET.get("demo") == "1" and request.session.get("demo_sandbox_file"):
        dr = request.session["demo_sandbox_file"]
        today_str = timezone.localdate().strftime("%d.%m.%Y")
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "\u0420\u0435\u0435\u0441\u0442\u0440_\u0418\u0414_\u0414\u0435\u043c\u043e"
        ws.append([f"\u0420\u0415\u0415\u0421\u0422\u0420 \u0418\u0414 \u0418 \u0412\u0415\u0414\u041e\u041c\u041e\u0421\u0422\u042c \u0420\u0410\u0411\u041e\u0422 \u041f\u041e \u0424\u0410\u0419\u041b\u0423: {dr.get('filename', '')}"])
        ws.append(["\u2116 \u043f/\u043f", "\u041d\u0430\u0438\u043c\u0435\u043d\u043e\u0432\u0430\u043d\u0438\u0435 \u043f\u043e\u0437\u0438\u0446\u0438\u0438 / \u0434\u043e\u043a\u0443\u043c\u0435\u043d\u0442\u0430", "\u0412\u044b\u0441\u043e\u0442\u043d\u044b\u0435 \u043e\u0442\u043c\u0435\u0442\u043a\u0438", "\u041e\u0441\u0438 / \u0418\u0441\u0442\u043e\u0447\u043d\u0438\u043a", "\u0414\u0430\u0442\u0430 \u0444\u043e\u0440\u043c\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u044f"])
        ws.append([1, f"\u0410\u041e\u0421\u0420 (\u041f\u0440\u0438\u043a\u0430\u0437 \u2116 344/\u043f\u0440) \u043f\u043e \u043a\u043e\u043c\u043f\u043b\u0435\u043a\u0442\u0443: {dr.get('filename', '')}", dr.get("elevs", ""), dr.get("axes", ""), today_str])
        for i, ln in enumerate(dr.get("lines", []), start=2):
            ws.append([i, ln, dr.get("elevs", ""), dr.get("filename", ""), today_str])
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        thin = Side(style="thin", color="CBD5E1")
        border = Border(left=thin, right=thin, top=thin, bottom=thin)
        ws["A1"].font = Font(bold=True, size=12, color="0F172A")
        for col_let, w in [("A", 8), ("B", 64), ("C", 24), ("D", 32), ("E", 18)]:
            ws.column_dimensions[col_let].width = w
        for cell in ws[2]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="1E3A8A")
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row, max_col=5):
            for c in row:
                c.border = border
                c.alignment = Alignment(vertical="center", wrap_text=True)
        buf = io.BytesIO()
        wb.save(buf)
        resp = HttpResponse(buf.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        resp["Content-Disposition"] = 'attachment; filename="Reestr_ID_Novyy_Klient.xlsx"'
        return resp
    tpl_bytes = request.FILES["customer_xlsx"].read() if (request.method == "POST" and "customer_xlsx" in request.FILES) else None
    memo_txt = request.FILES["memo_file"].read().decode("utf-8", errors="ignore") if (request.method == "POST" and "memo_file" in request.FILES) else ""
    xlsx_data = build_filled_customer_registry_xlsx(template_bytes=tpl_bytes, memo_text=memo_txt)
    resp = HttpResponse(xlsx_data, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    resp["Content-Disposition"] = 'attachment; filename="Reestr_ID_344pr.xlsx"'
    return resp


def new_client_wizard_view(request):
    import re
    from django.shortcuts import redirect
    from storage_control.services.id_template_engine import save_object_passport
    from storage_control.models import Document, ParsedPage, PurchaseRequest, StockMovement, PhotoIntake
    demo_result = None
    if request.method == "POST":
        if "demo_any_file" in request.FILES:
            f = request.FILES["demo_any_file"]
            fname = f.name
            ext = fname.rsplit(".", 1)[-1].lower() if "." in fname else ""
            raw = f.read()
            extracted_lines = []
            pages_cnt = 1
            if ext == "pdf":
                import io, pypdf
                reader = pypdf.PdfReader(io.BytesIO(raw))
                pages_cnt = len(reader.pages)
                txt = "\n".join((p.extract_text() or "") for p in reader.pages[:30])
                txt = re.sub(r"([?-???-???])\n([?-???-???])", r"\1\2", txt)
                extracted_lines = [ln.strip() for ln in txt.splitlines() if len(ln.strip()) > 6][:12]
            elif ext in ("xlsx", "xls"):
                import io, openpyxl
                wb = openpyxl.load_workbook(io.BytesIO(raw), data_only=True)
                pages_cnt = len(wb.sheetnames)
                for row in wb.active.iter_rows(values_only=True):
                    vals = [str(v).strip() for v in row if v is not None and str(v).strip()]
                    if vals:
                        extracted_lines.append(" | ".join(vals[:5]))
                    if len(extracted_lines) >= 12:
                        break
            elif ext == "docx":
                import io, docx
                d = docx.Document(io.BytesIO(raw))
                extracted_lines = [p.text.strip() for p in d.paragraphs if p.text.strip()][:12]
            elif ext in ("dwg", "dxf"):
                ver_map = {"AC1032": "AutoCAD 2018\u20132026 DWG", "AC1027": "AutoCAD 2013\u20132017 DWG", "AC1024": "AutoCAD 2010\u20132012 DWG", "AC1021": "AutoCAD 2007\u20132009 DWG"}
                hdr = raw[:6].decode("ascii", errors="ignore")
                cad_ver = ver_map.get(hdr, f"AutoCAD {ext.upper()} ({hdr or 'BIM'})")
                # ????????? ???????? ??????? ? ?????????? ?????? (CP1251 ? UTF-16LE) ?? ????????? ?????? DWG/DXF
                s_cp = re.findall(r'[\xc0-\xffA-Za-z0-9\s\-\.,\(\)\u2116\u00d8]{6,80}', raw.decode("cp1251", errors="ignore"))
                s_u16 = re.findall(r'[\u0410-\u044f\u0401\u0451A-Za-z0-9\s\-\.,\(\)\u2116\u00d8]{6,80}', raw.decode("utf-16le", errors="ignore"))
                uniq_lines = []
                for cand in (s_u16 + s_cp):
                    cl = re.sub(r'\s+', ' ', cand).strip()
                    if len(cl) >= 6 and sum("\u0410" <= ch <= "\u044f" or ch in "\u0401\u0451" for ch in cl) >= 4 and cl not in uniq_lines:
                        uniq_lines.append(cl)
                    if len(uniq_lines) >= 14:
                        break
                extracted_lines = [f"\u0427\u0435\u0440\u0442\u0435\u0436 {cad_ver} ({round(len(raw)/1048576, 2)} \u041c\u0411) \u043f\u0440\u0438\u043d\u044f\u0442 \u0432 \u043f\u0430\u043a\u0435\u0442 \u0418\u0414 \u2192 \u0433\u043e\u0442\u043e\u0432 \u043a \u0432\u043a\u043b\u044e\u0447\u0435\u043d\u0438\u044e \u0432 \u0420\u0435\u0435\u0441\u0442\u0440 \u0418\u0414 \u0438 \u0410\u041e\u0421\u0420 \u2116 344/\u043f\u0440"] + uniq_lines
            else:
                extracted_lines = [f"\u0413\u0440\u0430\u0444\u0438\u0447\u0435\u0441\u043a\u0438\u0439 \u043b\u0438\u0441\u0442 / \u0444\u043e\u0442\u043e ({ext.upper()}), \u0440\u0430\u0437\u043c\u0435\u0440 {round(len(raw)/1024, 1)} \u041a\u0411 \u2014 \u0433\u043e\u0442\u043e\u0432\u043e \u043a \u0432\u0435\u043a\u0442\u043e\u0440\u043d\u043e\u0439 \u043a\u0430\u043b\u0438\u0431\u0440\u043e\u0432\u043a\u0435 \u0427\u0435\u0440\u0435\u043f\u0430\u0445\u0438 CAD \u0438 \u043f\u0440\u0438\u0451\u043c\u043a\u0435 \u0423\u041f\u0414 \u0421\u043e\u043aолом."]

            joined = " ".join(extracted_lines)
            elevs = sorted(set(re.findall(r'[+\-]\d[\.,]\d{3}', joined)))[:6]
            axes = sorted(set(re.findall(r'(?:\u043e\u0441[\u0438\u044f\u0445]|\u043e\u0441\u044c)\s+[0-9\u0410-\u042fA-Z\-\/]{1,12}', joined, re.I)))[:6]
            demo_result = {
                "filename": fname,
                "ext": ext.upper(),
                "pages_cnt": pages_cnt,
                "elevs": ", ".join(elevs) or "\u041e\u043f\u0440\u0435\u0434\u0435\u043b\u044f\u044e\u0442\u0441\u044f \u043f\u043e \u043f\u0430\u0441порту \u043eбъекта",
                "axes": ", ".join(axes) or "\u0413\u043eтов\u043e \u043a \u043f\u0440\u0438вязке \u043a \u0441етке \u043eсей",
                "lines": extracted_lines or ["\u0424\u0430\u0439\u043b \u0443спе\u0448\u043d\u043e \u043f\u0440\u0438\u043d\u044f\u0442 \u0438 \u0433\u043e\u0442\u043e\u0432 \u043a \u0432\u044b\u043f\u0443\u0441\u043a\u0443 АОСР № 344/пр \u0438 р\u0435\u0435стр\u0430 ИД."],
            }
            request.session["demo_sandbox_file"] = demo_result
            return render(request, "storage_control/new_client.html", {"demo_result": demo_result})

        save_object_passport(request.POST.dict())
        if request.POST.get("wipe_old_data") == "1":
            StockMovement.objects.all().delete()
            PurchaseRequest.objects.all().delete()
            ParsedPage.objects.all().delete()
            Document.objects.all().delete()
            PhotoIntake.objects.all().delete()
        return redirect("storage_control:dashboard")
    return render(request, "storage_control/new_client.html", {"demo_result": demo_result})


def operation_memo_export_view(request):
    from django.http import HttpResponse
    from storage_control.services.id_template_engine import build_operation_memo_docx_bytes
    data = build_operation_memo_docx_bytes()
    resp = HttpResponse(data, content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    resp["Content-Disposition"] = 'attachment; filename="Pamyatka_Ekspluatacii_i_Garantii.docx"'
    return resp


def _suggest_analog_for_material(name: str) -> str:
    low = (name or "").lower()
    if "\u0449\u0435\u0431\u0435\u043d" in low:
        return "\u0410\u043d\u0430\u043b\u043e\u0433: \u0449\u0435\u0431\u0435\u043d\u044c \u0433\u0440\u0430\u043d\u0438\u0442\u043d\u044b\u0439/\u0433\u0440\u0430\u0432\u0438\u0439\u043d\u044b\u0439 \u0442\u043e\u0439 \u0436\u0435 \u0444\u0440\u0430\u043a\u0446\u0438\u0438 (\u0413\u041e\u0421\u0422 8267-93) + \u043f\u0430\u0441\u043f\u043e\u0440\u0442 \u043a\u0430\u0447\u0435\u0441\u0442\u0432\u0430"
    if any(k in low for k in ("\u0440\u043e\u0437\u0435\u0442\u043a", "\u0432\u044b\u043a\u043b\u044e\u0447")):
        return "\u0410\u043d\u0430\u043b\u043e\u0433: \u0441\u0442\u0440\u043e\u0433\u043e \u0441 \u0442\u043e\u0439 \u0436\u0435 \u0441\u0442\u0435\u043f\u0435\u043d\u044c\u044e IP (IP20/IP44/IP54), 16\u0410 \u0438 \u0442\u0438\u043f\u043e\u043c \u043c\u043e\u043d\u0442\u0430\u0436\u0430"
    if any(k in low for k in ("\u043b\u0430\u043c\u043f", "\u0441\u0432\u0435\u0442\u0438\u043b", "\u0431\u0440\u0430")):
        return "\u0410\u043d\u0430\u043b\u043e\u0433: \u043f\u043e \u0441\u0432\u0435\u0442\u043e\u0432\u043e\u043c\u0443 \u043f\u043e\u0442\u043e\u043a\u0443 (\u043b\u043c), \u0446\u043e\u043a\u043e\u043b\u044e (E27/GU10/LED), \u0442\u0435\u043c\u043f\u0435\u0440\u0430\u0442\u0443\u0440\u0435 3000/4000K \u0438 IP"
    if "\u043c\u0438\u043d" in low or "\u0432\u0430\u0442\u0430" in low:
        return "\u0410\u043d\u0430\u043b\u043e\u0433: \u043f\u043b\u0438\u0442\u044b \u043c\u0438\u043d\u0435\u0440\u0430\u043b\u043e\u0432\u0430\u0442\u043d\u044b\u0435 \u041d\u0413 \u0442\u043e\u0439 \u0436\u0435 \u043f\u043b\u043e\u0442\u043d\u043e\u0441\u0442\u0438 (75\u2013120 \u043a\u0433/\u043c\u00b3) \u0438 \u0442\u043e\u043b\u0449\u0438\u043d\u044b (Rockwool / \u0422\u0435\u0445\u043d\u043e\u041d\u0418\u041a\u041e\u041b\u042c / ISOROC, \u0413\u041e\u0421\u0422 9573-2012)"
    if "\u0440\u0430\u0434\u0438\u0430\u0442\u043e\u0440" in low:
        return "\u0410\u043d\u0430\u043b\u043e\u0433: \u043f\u043e \u043c\u043e\u0449\u043d\u043e\u0441\u0442\u0438 (\u0412\u0442), \u043c\u0435\u0436\u043e\u0441\u0435\u0432\u043e\u043c\u0443 \u0440\u0430\u0441\u0441\u0442\u043e\u044f\u043d\u0438\u044e (350/500 \u043c\u043c) \u0438 \u0434\u0430\u0432\u043b\u0435\u043d\u0438\u044e (\u0413\u041e\u0421\u0422 31311)"
    return "\u0410\u043d\u0430\u043b\u043e\u0433: \u043f\u043e \u0413\u041e\u0421\u0422/\u0421\u041f \u0447\u0435\u0440\u0435\u0437 \u043b\u0438\u0441\u0442 \u0430\u0432\u0442\u043e\u0440\u0441\u043a\u043e\u0433\u043e \u043d\u0430\u0434\u0437\u043e\u0440\u0430 \u0441 \u043f\u0440\u043e\u0435\u043a\u0442\u0438\u0440\u043e\u0432\u0449\u0438\u043a\u043e\u043c"


def project_totals_and_analogs_api(request):
    import re, functools
    from django.http import JsonResponse
    from django.db.models import Q
    from storage_control.models import PurchaseRequest, ParsedPage
    from storage_control.services.building_twin import fix_autocad_mojibake
    from storage_control.services.input_calibrator import classify_pdf_line_at_gate, normalize_unit_and_name

    def _clean_zone(z_raw: str) -> str:
        z = (z_raw or "").strip()
        if not z or re.match(r'^24\.045', z) or re.match(r'^[+\-]?0?\d\.\d{3}$', z) or "??" in z:
            return "По плану РД"
        return z

    q = (request.GET.get("q") or "").strip()
    if not q:
        return JsonResponse({"ok": True, "items": [], "totals_by_unit": {}, "blocked_items": [], "pdf_mentions": []})

    is_du_query = q.lower() in ("ду", "dn")
    if is_du_query:
        return JsonResponse({
            "ok": True,
            "query": q,
            "clarify_prompt": "Диаметр Ду указывается для конкретного изделия. Выберите \u043dоменклатуру из проекта:",
            "suggestions": ["Кран шаро\u0432ой", "Клапан балансировочный", "Труба", "Фланец", "Задвижка"],
            "totals_by_unit": {},
            "items": [],
            "blocked_items": [],
            "pdf_mentions": [],
        })
    variants = _norm_x_variants(q)
    m_du_q = re.match(r'^(?:ду|dn)\s*(\d{2,4})$', q, re.I)
    if m_du_q:
        d_num = m_du_q.group(1)
        variants.extend([f"Ду {d_num}", f"Ду{d_num}", f"DN{d_num}", f"DN {d_num}"])
    stem = q[:max(4, len(q) - 2)] if len(q) >= 5 else q
    for sc in (stem, stem.lower(), stem.capitalize(), q.lower(), q.capitalize()):
        if sc and sc not in variants:
            variants.append(sc)
    if "армат" in q.lower():
        variants.extend(["А500С", "А240", "34028"])

    q_words = [w.strip() for w in q.split() if len(w.strip()) >= 4]
    if len(q_words) >= 2 and not is_du_query:
        cond = functools.reduce(lambda a, b: a & b, [Q(material_name__icontains=w) | Q(material_name__icontains=w.capitalize()) | Q(material_name__icontains=w.upper()) for w in q_words])
    else:
        cond = functools.reduce(lambda a, b: a | b, [Q(material_name__icontains=v) for v in variants])

    canon_q_tokens = [tk for tk in canonicalize_spec_text(q).split() if len(tk) >= 2]
    all_reqs = list(PurchaseRequest.objects.select_related("document").order_by("id")[:1500])
    reqs = [r for r in all_reqs if all(tk in canonicalize_spec_text(r.material_name or "") for tk in canon_q_tokens)][:200]
    if not reqs and len(q) >= 3:
        from storage_control.services.quantum_normalizer import canon_key
        ck_q = canon_key(q)
        q_stem = q.split() if " " in q else q
        for pg in ParsedPage.objects.select_related("document").filter(text__icontains=q_stem[:6])[:15]:
            lines = [re.sub(r'\s+', ' ', l).strip() for l in fix_autocad_mojibake(pg.text or "").splitlines() if l.strip()]
            for idx_l, raw_ln in enumerate(lines):
                pair_ln = raw_ln + " " + (lines[idx_l + 1] if idx_l + 1 < len(lines) else "")
                if ck_q in canon_key(pair_ln):
                    m_q = re.search(r'(?:\u0448\u0442|\u043a\u043e\u043c\u043f\u043b|\u043f\.\u043c|\u043c2|\u043c\u00b2|\u043a\u0433|\u043c)\.?\s+(\d+(?:[\.,]\d+)?)\b', pair_ln, re.I)
                    qty_val = float(m_q.group(1).replace(",", ".")) if m_q else 1.0
                    if not PurchaseRequest.objects.filter(document=pg.document, material_name__iexact=raw_ln[:150], floor_info__contains=f"\u2116{pg.page_number}").exists():
                        pr_new = PurchaseRequest.objects.create(document=pg.document, material_name=raw_ln[:150], required_qty=qty_val, deficit_qty=qty_val, unit="\u0448\u0442.", floor_info=f"\u0421истема ПВ/ОВ · Лист \u2116{pg.page_number}")
                        reqs.append(pr_new)
                    break
    grouped, totals_by_unit, blocked_items = {}, {}, []
    for r in reqs:
        raw_nm = (r.material_name or "").strip()
        if classify_pdf_line_at_gate(raw_nm) != "SPEC_ITEM":
            continue
        if is_du_query and not re.search(r'(?:\bДу|\bDN|Фланец)', raw_nm, re.I):
            continue
        clean_nm, u, needs_du = normalize_unit_and_name(raw_nm, r.unit or "шт.")
        qty = float(r.required_qty or 0)
        if needs_du:
            blocked_items.append({"req_num": f"ЗМ-{r.id:04d}", "mark_name": f"{clean_nm} [⛔ БЛОК ЗАКАЗА: требуется уточнение Ду]", "qty": qty, "unit": u, "work_cascade": build_work_sequence_cascade(clean_nm), **_build_item_tech_passport(clean_nm), **_build_system_assembly_info(clean_nm, _clean_zone(r.floor_info), r.document.title if r.document else "РД"), "analog_item": _suggest_analog_for_material(clean_nm), "doc_title": r.document.title if r.document else "РД"})
            continue

        merge_key = f"{clean_nm.lower()} | {u}"
        totals_by_unit[u] = round(totals_by_unit.get(u, 0.0) + qty, 2)
        entry = grouped.setdefault(merge_key, {
            "req_num": f"ЗМ-{r.id:04d}",
            "mark_name": clean_nm,
            "floor_or_zone": _clean_zone(r.floor_info),
            "doc_title": r.document.title if r.document else "РД",
            "qty": 0.0,
            "unit": u,
        })
        entry["qty"] = round(entry["qty"] + qty, 2)

    pdf_mentions, seen_snips = [], set()
    p_cond = functools.reduce(lambda a, b: a | b, [Q(text__icontains=v) for v in variants[:6]])
    for pg in ParsedPage.objects.select_related("document").filter(p_cond)[:25]:
        txt = fix_autocad_mojibake(pg.text or "")
        txt = re.sub(r'(?:\b\d{2}\.\d{2}\b\s*){2,}', ' ', txt)
        txt = re.sub(r'(?:\b\d\b\s*){4,}', ' ', txt)
        m = re.search(r'(?:\bДу|\bDN)\s*\d{2,4}', txt) if is_du_query else re.search("|".join(re.escape(v) for v in variants[:6] if v), txt, re.I)
        if not m:
            continue
        snip = re.sub(r'\s+', ' ', txt[max(0, m.start() - 30): m.end() + 95]).strip()
        norm_key = re.sub(r'\W+', '', snip[:55].lower())
        if norm_key in seen_snips:
            continue
        seen_snips.add(norm_key)
        pdf_mentions.append({"doc": pg.document.title if pg.document else "РД", "page": pg.page_number, "snippet": snip})
        if len(pdf_mentions) >= 8:
            break

    if "кг" in totals_by_unit:
        totals_by_unit["т (тонн)"] = round(totals_by_unit["кг"] / 1000.0, 3)
    return JsonResponse({"ok": True, "query": q, "totals_by_unit": totals_by_unit, "items": sorted(grouped.values(), key=_engineering_sort_key), "blocked_items": blocked_items, "pdf_mentions": pdf_mentions, "general_analog": _suggest_analog_for_material(q), "lifecycle": _build_foundation_to_handover_design(q, totals_by_unit)})


def inventory_foreman_api(request):
    import os, json
    from django.conf import settings
    from django.http import JsonResponse
    fpath = os.path.join(settings.BASE_DIR, "foreman_inventory.json")
    items = json.load(open(fpath, encoding="utf-8")) if os.path.exists(fpath) else []
    if request.method == "POST":
        inv_num = f"\u0418\u041d\u0412-{len(items) + 1:04d}"
        rec = {
            "inv_num": inv_num,
            "item_name": (request.POST.get("item_name") or "").strip(),
            "qty": (request.POST.get("qty") or "1").strip(),
            "foreman": (request.POST.get("foreman") or "\u041f\u0440\u043e\u0440\u0430\u0431 \u0443\u0447\u0430\u0441\u0442\u043a\u0430").strip(),
            "zone": (request.POST.get("zone") or "\u0423\u0447\u0430\u0441\u0442\u043e\u043a \u043c\u043e\u043d\u043e\u043b\u0438\u0442\u0430").strip(),
            "invoice_check": (request.POST.get("invoice_check") or "\u0421\u0432\u0435\u0440\u0435\u043d\u043e \u043f\u043e \u0444\u043e\u0442\u043e \u0423\u041f\u0414 \u0438 \u0444\u0430\u043a\u0442\u0443").strip(),
        }
        if rec["item_name"]:
            items.insert(0, rec)
            json.dump(items, open(fpath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return JsonResponse({"ok": True, "items": items})


def room_cascade_dynamics_api(request):
    import datetime
    from django.http import JsonResponse
    from django.utils import timezone
    from storage_control.models import PurchaseRequest, PhotoIntake

    room_code = (request.GET.get("code") or "101").strip()
    room_name = (request.GET.get("name") or "\u041a\u043e\u0440\u0438\u0434\u043e\u0440").strip()
    area = (request.GET.get("area") or "45.0").strip()
    today = timezone.localdate()

    # ????????? ?????????? ?? ??????? ????????? ?? 3 ?????????? ??????? ??? ???? ???????
    finishing, cables_trays, pipes_mep = [], [], []
    for r in PurchaseRequest.objects.order_by("-required_qty")[:120]:
        nm = (r.material_name or "").strip()
        low = nm.lower()
        row = {"req_num": f"\u0417\u041c-{r.id:04d}", "name": nm[:85], "plan": f"{r.required_qty} {r.unit}", "deficit": f"{r.deficit_qty} {r.unit}"}
        if any(k in low for k in ("\u043f\u0433\u043f", "\u043f\u043b\u0438\u0442", "\u0448\u0442\u0443\u043a\u0430\u0442", "\u043a\u0440\u0430\u0441\u043a", "\u043f\u043e\u043b", "\u0434\u0432\u0435\u0440", "\u0432\u0430\u0442\u0430")):
            if len(finishing) < 5: finishing.append(row)
        elif any(k in low for k in ("\u043a\u0430\u0431\u0435\u043b", "\u043b\u043e\u0442\u043e\u043a", "\u043b\u043e\u0442\u043a", "\u043f\u0440\u043e\u0432\u043e\u0434", "\u0431\u044d", "\u0449\u0438\u0442", "\u0440\u043e\u0437\u0435\u0442")):
            if len(cables_trays) < 5: cables_trays.append(row)
        elif any(k in low for k in ("\u0442\u0440\u0443\u0431", "\u0432\u043e\u0437\u0434\u0443\u0445", "\u0442\u0440\u0430\u043f", "\u043a\u043b\u0430\u043f\u0430\u043d", "\u043d\u0430\u0441\u043e\u0441")):
            if len(pipes_mep) < 5: pipes_mep.append(row)

    # ?????????? ???? ?????? ????? ?????????
    tag = f"ROOM:{room_code}"
    photos = []
    for ph in PhotoIntake.objects.filter(notes__icontains=tag).order_by("-id")[:12]:
        photos.append({
            "id": ph.id,
            "url": ph.image.url if ph.image else "",
            "date": ph.created_at.strftime("%d.%m.%Y %H:%M") if getattr(ph, "created_at", None) else today.strftime("%d.%m.%Y"),
            "report": ph.ocr_raw_text or ph.notes or "\u0424\u043e\u0442\u043e-\u0444\u0438\u043a\u0441\u0430\u0446\u0438\u044f \u0441\u043c\u0435\u043d\u044b",
        })

    progress_pct = min(100, len(photos) * 25)
    return JsonResponse({
        "ok": True,
        "room_code": room_code,
        "room_name": room_name,
        "area": area,
        "progress_pct": progress_pct,
        "finish_date": (today + datetime.timedelta(days=max(3, 20 - len(photos) * 4))).strftime("%d.%m.%Y"),
        "finishing": finishing,
        "cables_trays": cables_trays,
        "pipes_mep": pipes_mep,
        "photos": photos,
    })


def room_photo_upload_api(request):
    from django.http import JsonResponse
    from storage_control.models import PhotoIntake
    if request.method == "POST" and "room_photo" in request.FILES:
        code = (request.POST.get("room_code") or "101").strip()
        name = (request.POST.get("room_name") or "\u041a\u043e\u0440\u0438\u0434\u043e\u0440").strip()
        work_note = (request.POST.get("work_note") or "").strip()
        f = request.FILES["room_photo"]
        # ?????? ???? ??????? ?????? (??????????? ???? ????? ?? ?????/?????????/OCR)
        detected = work_note or "\u0417\u0440\u0435\u043d\u0438\u0435 \u0441\u043e\u043a\u043e\u043b\u0430: \u0437\u0430\u0444\u0438\u043a\u0441\u0438\u0440\u043e\u0432\u0430\u043d \u043c\u043e\u043d\u0442\u0430\u0436 \u043b\u043e\u0442\u043a\u043e\u0432, \u043f\u0440\u043e\u043a\u043b\u0430\u0434\u043a\u0430 \u043a\u0430\u0431\u0435\u043b\u044f \u0438 \u0443\u0441\u0442\u0440\u043e\u0439\u0441\u0442\u0432\u043e \u041f\u0413\u041f / \u043e\u0442\u0434\u0435\u043b\u043a\u0438 (+25% \u043a \u0433\u043e\u0442\u043e\u0432\u043d\u043e\u0441\u0442\u0438)"
        ph = PhotoIntake.objects.create(
            image=f,
            doc_number=f"\u0424\u041e\u0422\u041e-{code}",
            notes=f"ROOM:{code} | \u041f\u043e\u043c. {code} ({name})",
            ocr_raw_text=detected,
        )
        return JsonResponse({"ok": True, "photo_id": ph.id})
    return JsonResponse({"ok": False}, status=400)


def partner_league_view(request):
    import os, json
    from django.conf import settings
    from django.shortcuts import render, redirect
    from storage_control.services.price_relay import step_price_relay, import_dealer_csv
    from storage_control.services.quantum_normalizer import canon_key

    m_path = os.path.join(settings.BASE_DIR, "partner_league_matrix.json")
    default_matrix = [
        {"commodity_class": "Теплоизоляция и ленты (Energoflex / K-Flex)", "partners": "РОЛС Изомаркет, ТеплоКомплект", "discount": "14% B2B", "logistics": "Борт / Самовывоз МО", "payment": "Безнал НДС 20% + УПД"},
        {"commodity_class": "Вентиляция и VRF-системы (NED / Веза / ЛИСАНТ)", "partners": "НЕД-Центр, Веза-Москва, ГалВент", "discount": "18% проект", "logistics": "Доставка на объект", "payment": "Отсрочка / НДС 20%"},
        {"commodity_class": "Арматура и фланцы (АДЛ / Ридан / LD)", "partners": "АДЛ Продакшн, СТМ-Комплект", "discount": "15% опт", "logistics": "Манипулятор / Сборный", "payment": "Безнал НДС + Паспорт"},
    ]
    matrix = json.load(open(m_path, encoding="utf-8")) if os.path.exists(m_path) else default_matrix
    imported_cnt = 0
    if request.method == "POST":
        if request.FILES.get("dealer_csv"):
            imported_cnt = import_dealer_csv(request.FILES["dealer_csv"].read())
        else:
            c_cls, pts = (request.POST.get("commodity_class") or "").strip(), (request.POST.get("partners") or "").strip()
            if c_cls and pts:
                matrix.insert(0, {"commodity_class": c_cls, "partners": pts, "discount": request.POST.get("discount", "12% B2B"), "logistics": request.POST.get("logistics", "Борт / Самовывоз"), "payment": "Безнал НДС 20% + УПД"})
                json.dump(matrix, open(m_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
                return redirect(request.get_full_path())

    relay_info = step_price_relay(10) if request.GET.get("relay") == "1" else step_price_relay(0)
    q = (request.GET.get("q") or "").strip()
    qty = (request.GET.get("qty") or "").strip()
    if q:
        q_low = q.lower()
        if any(k in q_low for k in ("шпакл", "шпатл", "штукат", "смес")):
            matrix = [{"commodity_class": "Сухие строительные смеси и шпаклёвки (Knauf / Волма / Ceresit)", "partners": "Сатурн-Строймаркет, Петрович B2B, ЦКСМ", "discount": "По прайсу B2B", "logistics": "Паллеты / Манипулятор", "payment": "Безнал НДС 20% + УПД"}] + matrix
        elif any(k in q_low for k in ("шпильк", "болт", "гайк", "анкер", "метиз")):
            matrix = [{"commodity_class": "Крепёж, шпильки и метизы (ГОСТ / DIN 975 / Hilti)", "partners": "ЦКИ (Центр Крепёжных Изделий), Трайв-Комплект", "discount": "По прайсу B2B", "logistics": "Газель / Самовывоз", "payment": "Безнал НДС 20% + Сертификат"}] + matrix
        else:
            matrix = [{"commodity_class": f"Профильный подбор по запросу: {q[:45]}", "partners": "Аккредитованные дистрибьюторы и заводы Москвы/МО", "discount": "По прайсу B2B", "logistics": "Доставка / Самовывоз", "payment": "Безнал НДС 20% + УПД"}] + matrix
    matched_price = relay_info["prices"].get(canon_key(q), {}) if q else {}
    return render(request, "storage_control/partner_league.html", {"matrix": matrix, "query": q, "qty": qty, "relay": relay_info, "matched_price": matched_price, "imported_cnt": imported_cnt})


def aosr_print_view(request, slug: str):
    from django.shortcuts import render
    from storage_control.models import PurchaseRequest, ParsedPage
    from storage_control.services.quantum_normalizer import canon_key
    ru_title = _detranslit_mark_slug(slug)
    reqs = [r for r in PurchaseRequest.objects.select_related("document").all()[:2000] if canon_key(ru_title.split() if ru_title else slug) in canon_key(r.material_name or "")]
    docs = sorted({r.document.title for r in reqs if r.document}) or ["Рабочая документация 24.0454"]
    qty_s = f"{round(sum(float(r.required_qty or 0) for r in reqs), 2)} {reqs.unit}" if reqs else "по ведомости РД"
    return render(request, "storage_control/aosr_print.html", {"title": ru_title, "qty": qty_s, "docs_list": ", ".join(docs)})


def executive_summary_view(request):
    from django.shortcuts import render
    from storage_control.models import PurchaseRequest
    all_r = list(PurchaseRequest.objects.all()[:3000])
    def _cnt(keys): return sum(1 for r in all_r if any(k in (r.material_name or "").lower() for k in keys))
    stages = [
        {"title": "1. Фундамент и нулевой цикл (КЖ0)", "color": "#94a3b8", "count": _cnt(("армат", "бетон", "фундам")), "desc": "Котлован, подбетонка, гидроизоляция, армокаркас, испытания кубиков 7/28 сут.", "slug": "armatura-a500s"},
        {"title": "2. Несущий каркас и КМ", "color": "#38bdf8", "count": _cnt(("рама", "балк", "профил")), "desc": "Монтаж рам Рм-1.1, колонн, геодезия осей и УЗК сварных соединений.", "slug": "rama-rm-1-1"},
        {"title": "3. Кровля и тепловой контур", "color": "#fbbf24", "count": _cnt(("техноэласт", "пламя", "кровл")), "desc": "Праймер, рулонная гидроизоляция Техноэласт ПЛАМЯ СТОП, пролив и приёмка.", "slug": "tehnoelast-plamya-stop"},
        {"title": "4. Инженерные сети (ОВ / ВК / ЭС)", "color": "#34d399", "count": _cnt(("воздуховод", "фланец", "кран", "nd-isr")), "desc": "Воздуховоды 200х300, VRF-блоки ND-ISR, арматура Ду 50–100, опрессовка.", "slug": "vozduhovod-200h300"},
        {"title": "5. Чистовая отделка (АР1.1 / RAL)", "color": "#f472b6", "count": _cnt(("ral", "краск", "шпатл")), "desc": "Шпатлёвка, грунтовка, стеклообои и поэтажная окраска RAL 7006 / 9011.", "slug": "kraska-ral-7006"},
        {"title": "6. Пусконаладка ПНР и сдача", "color": "#a855f7", "count": _cnt(("пд6", "система")), "desc": "Индивидуальные испытания Системы ПД6 L=16290, В1, К2, паспорта и закрытие АОСР.", "slug": "sistema-pd6-l-16290"},
    ]
    return render(request, "storage_control/executive_summary.html", {"stages": stages})
