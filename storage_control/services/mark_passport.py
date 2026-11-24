# -*- coding: utf-8 -*-
import re
import urllib.parse
import urllib.request
from django.core.cache import cache
from storage_control.models import Document, PurchaseRequest, WarehouseTmc, BimCrossLink

_TRANSLIT = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
    'ы': 'y', 'э': 'e', 'ю': 'yu', 'я': 'ya',
}


def make_mark_slug(title: str) -> str:
    """Генерирует чистый SEO-алиас (slug) для https:// (например: bordyur-br-100-20-8)."""
    s = "".join(_TRANSLIT.get(ch, ch) for ch in (title or "").lower())
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    return s[:80] or "pozitsiya-rd"


def _fetch_web_analogs(mark_title: str) -> list:
    """Динамически ищет аналоги и эквиваленты в открытых справочниках для любой незнакомой марки."""
    cache_key = f"eng_analogs_{hash(mark_title)}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    found = []
    try:
        clean_q = re.sub(r'\([^\)]*\)', '', mark_title).strip()[:60]
        q_enc = urllib.parse.quote(f"{clean_q} аналог эквивалент замена характеристики")
        req = urllib.request.Request(
            f"https://duckduckgo.com{q_enc}",
            headers={"User-Agent": "Mozilla/5.0"},
        )
        html = urllib.request.urlopen(req, timeout=4).read().decode("utf-8", errors="ignore")
        for m in re.finditer(r'class="result__snippet"[^>]*>(.*?)</a>', html, re.S | re.I):
            txt = re.sub(r'<[^>]+>', '', m.group(1)).strip()
            txt = re.sub(r'\s+', ' ', txt)
            if len(txt) > 25 and txt not in found:
                found.append(txt[:220])
            if len(found) >= 3:
                break
    except Exception:
        pass
    cache.set(cache_key, found, 7200)
    return found


def _decode_engineering_mark(mark_title: str) -> dict:
    """Полный инженерный декодер марок и подбор проверенных аналогов по ГОСТ."""
    low = (mark_title or "").lower()

    if "бордюр" in low or "бр " in low:
        is_road = "300" in low or "30.15" in low
        return {
            "category": "Дорожное строительство и благоустройство (ГОСТ 6665-91)",
            "decoded": (
                "Бордюрный камень дорожный (БР 100.30.15), 1000×300×150 мм, масса ~96 кг."
                if is_road
                else "Бордюрный камень тротуарный/рядовой (БР 100.20.8), 1000×200×80 мм, масса ~36 кг."
            ),
            "physics": "Серый цвет — чистый портландцемент без красителей (максимальная морозостойкость F200). Скос отводит ливневую воду и защищает кромку от наезда колеса.",
            "field_tips": [
                "Ставить на уплотнённое щебёночно-песчаное основание (h=100–150 мм) и бетонную подушку B15.",
                "Обязательно устроить бетонные «замки» с обеих сторон высотой 100–120 мм от опрокидывания и пучения.",
                "Температурные швы 3–5 мм заполнять цементно-песчаным раствором М150.",
            ],
            "analogs": ["БР 100.30.18 (усиленный магистральный, 118 кг)", "БВ 100.30.15 (въездной с понижением)"],
        }

    if any(w in low for w in ("клеев", "раствор ytong", "клей для газобетона")):
        return {
            "category": "Кладочные клеевые смеси для ячеистого бетона (ГОСТ 31357-2007)",
            "decoded": f"Тонкошовный полимерцементный клей для газобетона: {mark_title} (толщина шва 1–3 мм).",
            "physics": "Исключает «мостики холода» и снижает расход смеси в 5 раз (расход ~25 кг / 1 мешок на 1 м³ блоков).",
            "field_tips": [
                "Наносить только зубчатым шпателем (зуб 4–6 мм) на обеспыленную поверхность блока.",
                "При температуре ниже +5 °C применять только зимний клей с противоморозными добавками (до -10 °C).",
            ],
            "analogs": [
                "Bonolit Клей для газобетона (25 кг, летний/зимний) — рецептура бывшего завода YTONG",
                "Ceresit CT 21 (клей для ячеистого бетона, 25 кг) — в наличии на всех базах Тулы",
                "Волма-Блок / Knauf Клей для газобетона (25 кг)",
            ],
        }

    if any(w in low for w in ("ytong", "газобетон")):
        return {
            "category": "Автоклавный газобетон (ГОСТ 31360-2007)",
            "decoded": f"Блок стеновой из автоклавного газобетона (D500, B2.5–B3.5, толщина 200 мм): {mark_title}.",
            "physics": "Геометрия 625×250×200 мм (расход 6,4 блока на 1 м² стены, 1 м³ = 5 м² стены 200 мм).",
            "field_tips": [
                "Первый ряд класть на ЦПР М150 по отсечной гидроизоляции; все последующие — на тонкошовный клей 2 мм.",
                "Армировать каждый 3–4-й ряд и подоконные зоны двумя прутками Ø8 А500С в штробах.",
            ],
            "analogs": [
                "Bonolit D500 B3.5 (625×250×200 мм) — выпускается на бывшем заводе YTONG (Можайск / Малоярославец)",
                "Калужский газобетон (КГБ D500, 625×250×200 мм) — ближайший завод к Туле",
                "ГРАС Калуга / AeroStone D500 (625×250×200 мм)",
            ],
        }

    if any(w in low for w in ("гидроэласт", "гидроизоляц")):
        return {
            "category": "Обмазочная эластичная гидроизоляция (ГОСТ Р 56378-2015)",
            "decoded": f"Эластичная полимерцементная / полимерная обмазочная гидроизоляция: {mark_title}.",
            "physics": "Перекрывает трещины раскрытием до 1–2 мм, образует бесшовную мембрану (расход ~1,5–2,5 кг/м² в 2 слоя).",
            "field_tips": [
                "Все внутренние углы и примыкания пол–стена проклеить гидроизоляционной лентой (Ceresit CL 152) между 1-м и 2-м слоем.",
                "Наносить в 2 перекрёстных слоя с выдержкой 3–4 часа между слоями.",
            ],
            "analogs": [
                "Ceresit CR 166 (двухкомпонентная эластичная гидроизоляция) или Ceresit CL 51 (под плитку)",
                "Knauf Флэхендихт / Weber.tec 822 — эластичная гидроизоляционная мастика (в наличии в Туле)",
                "Mapei Mapelastic / Litokol Hidroflex",
            ],
        }

    if any(w in low for w in ("цементном вяжущем", "блок строительный", "стеновой камень", "керамзитобетон")):
        return {
            "category": "Стеновые камни и перегородки (ГОСТ 6133-2019)",
            "decoded": "Камень стеновой бетонный / керамзитобетонный на цементном вяжущем, толщина 200 мм (390×190×188 мм, ~12,5 шт./м²).",
            "physics": "Влагостойкий, морозостойкий (F50–F100) и негорючий (НГ) — обязателен для подвалов, венткамер, ИТП и электрощитовых.",
            "field_tips": [
                "Первый ряд кладки укладывать по рулонной гидроизоляции на ЦПР М100–М150.",
                "Армировать горизонтальные швы сеткой Ø3–4 мм Вр-1 через каждые 3–4 ряда и анкеровать к колоннам.",
            ],
            "analogs": [
                "Керамзитобетонный блок КББ 390×190×188 мм (М75–М100, ГОСТ 6133-2019)",
                "Бетонный / пескобетонный камень СКЦ 390×190×188 мм (М100–М150, ГОСТ 6133-2019) — огнестойкость EI150",
                "Силикатный перегородочный блок 498×248×188 мм (ГОСТ 379-2015)",
            ],
        }

    if any(w in low for w in ("пазогребнев", "пгп")):
        return {
            "category": "Перегородки из пазогребневых плит (ГОСТ 6428-2018)",
            "decoded": f"Плита пазогребневая гипсовая (ПГП) полнотелая: {mark_title} (667×500×100 мм, ~3 плиты на 1 м²).",
            "physics": "Применяется в сухих помещениях; для влажных зон и техпомещений требуется влагостойкая ПГПВ (зелёная).",
            "field_tips": [
                "Первый ряд укладывать на основание через упругую звукоизоляционную прокладку.",
                "Склейка гребень-паз выполняется на гипсовый монтажный клей (Knauf Перлфикс / Волма Монтаж).",
            ],
            "analogs": [
                "Knauf ПГП полнотелая 667×500×100 мм (ГОСТ 6428-2018)",
                "Волма ПГП полнотелая 667×500×100 мм — прямой эквивалент",
                "Гипсополимер / Magma ПГП 100 мм",
            ],
        }

    if any(w in low for w in ("герметик", "огнетитан")):
        return {
            "category": "Противопожарная герметизация швов и проходок (ФЗ-123)",
            "decoded": f"Огнестойкий силиконовый герметик (класс НГ / EI180–EI240): {mark_title}.",
            "physics": "Не поддерживает горение (НГ), сохраняет эластичность при деформации швов до 25%.",
            "field_tips": [
                "Глубина заполнения шва — 0,5 от его ширины по уплотняющему шнуру Вилатерм.",
                "Обязательно приложить пожарный сертификат (ФЗ-123) к Акту АОСР!",
            ],
            "analogs": [
                "Hilti CFS-S SIL (огнестойкий силиконовый герметик EI240)",
                "Nullifire FS703 / Sika Firesil Marine N",
                "ТехноНИКОЛЬ Огнестойкий силиконовый герметик (сертификат НГ)",
            ],
        }

    if any(w in low for w in ("муфта", "пквнтп", "пзэми")):
        return {
            "category": "Кабельная арматура 0,4–1 кВ (ГОСТ 13781.0-86)",
            "decoded": f"Концевая термоусаживаемая муфта для бронированного кабеля: {mark_title}.",
            "physics": "Обеспечивает герметизацию разделки жил, заземление стальной брони и защиту от пробоя.",
            "field_tips": [
                "Закрепить проводник заземления на бронеленты кабеля пружиной постоянного давления.",
                "Усадку трубок вести от середины к краям без перегрева изоляции.",
            ],
            "analogs": [
                "КВТ 5ПКВТпБ-70/120 (термоусаживаемая муфта с болтовыми наконечниками — прямой аналог ПЗЭМИ)",
                "Прогресс / НИЛЕД 5ПКВТпБ-70/120",
                "Raychem (TE Connectivity) POLJ-12/5x70-120",
            ],
        }

    if any(w in low for w in ("подвес", "страт", "ostec", "лоток")):
        return {
            "category": "Кабеленесущие системы и монтажный профиль (СТРАТ 41×41)",
            "decoded": f"С-образный монтажный профиль 41×41 мм с защитным цинковым покрытием: {mark_title}.",
            "physics": "Стандартный шаг перфорации 41×41 мм позволяет стыковать консоли и подвесы разных заводов без переделки узла.",
            "field_tips": [
                "Срезы оцинкованного профиля на объекте обработать холодным цинкованием.",
                "Шаг установки потолочных подвесов при кабельной нагрузке — не более 1,5–2,0 м.",
            ],
            "analogs": [
                "DKC B5 Combitech (профиль монтажный BPM-41 / BPL-41, толщ. 2,5 мм — 100% совместим с OSTEC)",
                "IEK LPR-41 (профиль СТРАТ 41×41×2,5 мм)",
                "Hilti MQ-41",
            ],
        }

    if any(w in low for w in ("110", "пнд", "пэ ", "футляр", "труб")):
        return {
            "category": "Трубопроводы ПНД / ПЭ и защитные футляры Ø110 мм (ГОСТ 18599-2001)",
            "decoded": f"Труба полиэтиленовая ПЭ100 / ПНД техническая или напорная (футляр кабельный / выпуск К1): {mark_title}.",
            "physics": "Кольцевая жёсткость SN8–SN16 (SDR 11 / SDR 17,6), рабочая температура от -40°C до +40°C, срок службы > 50 лет.",
            "field_tips": [
                "Укладывать в траншею на песчаную подушку толщиной не менее 100–150 мм без камней и строительного мусора.",
                "Торцы кабельных футляров Ø110 мм после протяжки кабеля загерметизировать термоусаживаемыми манжетами или уплотнителем.",
            ],
            "analogs": [
                "ПОЛИПЛАСТИК ПЭ100 SDR 17 / SDR 11 Ø110 мм (ГОСТ 18599-2001) — завод в Тульской обл. (Новомосковск)",
                "ИКАПЛАСТ / Техстрой ПЭ100 Ø110 мм — прямой эквивалент для кабельных футляров и НВК",
                "Ostendorf KGEM Ø110×3,2 мм SN8 (для самотечной канализации К1)",
            ],
        }


    web_analogs = _fetch_web_analogs(mark_title)
    return {
        "category": "Инженерное оборудование и ТМЦ (Динамический подбор)",
        "decoded": f"Проектная позиция: {mark_title}",
        "physics": "Поставляется партиями с паспортом качества и сертификатом соответствия.",
        "field_tips": [
            "Сверить маркировку, габариты и комплектность на бирке завода с ведомостью РД при разгрузке.",
            "Подшить скан паспорта качества в Журнал актов АОСР до закрытия скрытых работ.",
        ],
        "analogs": web_analogs or ["Подбор эквивалента по согласованию с авторским надзором (ГИП)"],
    }


def _fetch_engineering_diagrams(query: str) -> list:
    cache_key = f"eng_imgs_{hash(query)}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    imgs = []
    try:
        q_enc = urllib.parse.quote(f"{query} схема монтажа чертеж")
        req = urllib.request.Request(
            f"https://bing.com{q_enc}&first=1",
            headers={"User-Agent": "Mozilla/5.0"},
        )
        html = urllib.request.urlopen(req, timeout=4).read().decode("utf-8", errors="ignore")
        for m in re.finditer(r'murl&quot;:&quot;(https?://[^&]+?\.(?:jpg|jpeg|png|webp))&quot;', html, re.I):
            url = m.group(1)
            if url not in imgs:
                imgs.append(url)
            if len(imgs) >= 4:
                break
    except Exception:
        pass
    cache.set(cache_key, imgs, 7200)
    return imgs


def build_mark_passport_data(query: str) -> dict:
    """Собирает полный Цифровой паспорт, аналоги, схемы img и сквозную историю Марки по всем томам."""
    clean_q = (query or "").strip()
    token = re.sub(r'\s*\([^\)]*\)', '', clean_q)[:24].strip()

    by_title = {}
    if len(token) >= 3:
        for doc in Document.objects.prefetch_related("pages").all().order_by("title"):
            matched_pages = [p.page_number for p in doc.pages.all() if token.lower() in (p.text or "").lower()]
            if matched_pages:
                entry = by_title.setdefault(doc.title, {"doc_title": doc.title, "revision": f"Рев. {doc.revision_num}", "pages": set()})
                entry["pages"].update(matched_pages)
    history_timeline = [
        {"doc_title": v["doc_title"], "revision": v["revision"], "pages": sorted(v["pages"])[:12]}
        for v in by_title.values()
    ]

    if len(token) >= 3:
        for doc in Document.objects.prefetch_related("pages").all().order_by("title"):
            matched_pages = [p.page_number for p in doc.pages.all() if token.lower() in (p.text or "").lower()]
            if matched_pages:
                history_timeline.append({
                    "doc_title": doc.title,
                    "revision": f"Рев. {doc.revision_num}",
                    "pages": matched_pages[:10],
                })

    reqs = list(PurchaseRequest.objects.filter(material_name__icontains=token[:18])[:5]) if len(token) >= 3 else []
    wh_items = list(WarehouseTmc.objects.filter(nomenclature__icontains=token[:18])[:3]) if len(token) >= 3 else []
    bim_links = list(BimCrossLink.objects.filter(bim_tag__icontains=token[:14])[:4]) if len(token) >= 3 else []

    return {
        "query": clean_q,
        "slug_alias": make_mark_slug(clean_q),
        "tech": _decode_engineering_mark(clean_q),
        "history_timeline": history_timeline,
        "requests": reqs,
        "warehouse": wh_items,
        "bim_links": bim_links,
        "diagrams": _fetch_engineering_diagrams(token or clean_q),
    }
