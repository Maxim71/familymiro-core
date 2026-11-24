# -*- coding: utf-8 -*-
import re
from decimal import Decimal
from storage_control.models import WarehouseTmc, PurchaseRequest
from storage_control.services.section_decoder import resolve_section_and_brigade

UNITS = r'(?:тыс\.?\s*шт\.?|пог\.?\s*м\.?|м\.?\s*п\.?|п\.?\s*м\.?|м2|м²|м3|м³|шт\.?|компл\.?|упак\.?|рул\.?|набор|пар|кг|т|л|м|ч|сут|мес)'

OKEI_CODE_MAP = {
    'м': ('м', '006'),
    'пог. м': ('пог. м', '018'),
    'п.м': ('пог. м', '018'),
    'п.м.': ('пог. м', '018'),
    'м.п': ('пог. м', '018'),
    'м.п.': ('пог. м', '018'),
    'м2': ('м²', '055'),
    'м²': ('м²', '055'),
    'м3': ('м³', '113'),
    'м³': ('м³', '113'),
    'л': ('л', '112'),
    'г': ('г', '163'),
    'кг': ('кг', '166'),
    'т': ('т', '168'),
    'квт·ч': ('кВт·ч', '245'),
    'гкал': ('Гкал', '233'),
    'ч': ('ч', '356'),
    'сут': ('сут', '359'),
    'мес': ('мес', '362'),
    'набор': ('набор', '704'),
    'пар': ('пар', '715'),
    'рул': ('рул.', '736'),
    'рул.': ('рул.', '736'),
    'упак': ('упак.', '778'),
    'упак.': ('упак.', '778'),
    'шт': ('шт.', '796'),
    'шт.': ('шт.', '796'),
    'тыс. шт': ('тыс. шт.', '798'),
    'тыс. шт.': ('тыс. шт.', '798'),
    'компл': ('компл.', '839'),
    'компл.': ('компл.', '839'),
}


def _normalize_okei_unit(raw_unit: str) -> tuple:
    """Возвращает (нормализованная_единица, код_ОКЕИ) по классификатору РФ."""
    key = re.sub(r'\s+', ' ', (raw_unit or "").strip().lower()).rstrip('.')
    if key in OKEI_CODE_MAP:
        return OKEI_CODE_MAP[key]
    if f"{key}." in OKEI_CODE_MAP:
        return OKEI_CODE_MAP[f"{key}."]
    return ((raw_unit or "шт.").strip(), "796")


ROOM_HEADER_RE = re.compile(
    r'^(0\d{2}|[1-9]\d{1,2}[а-яёa-z]?)\s+([А-ЯЁ][А-ЯЁа-яё\s\-\(\)]{2,55})$'
)

# Барьер 2: Защита технических параметров (Ø200, DN150, h=0, отм., шаг) от подмены на количество
TECH_PARAM_TAIL_RE = re.compile(r'(?:Ø|ø|Ду|DN|PN|[hHBtδL]\s*=|отм\.?|шаг|М|В)\s*$', re.IGNORECASE)
# Короткие буквенные коды схем (КА, КВ, QF, QS, HL, SB, ТТ)
SCHEMATIC_TAG_RE = re.compile(r'^(?:[A-ZА-ЯЁ]{1,4}\d{0,3}(?:[\.\-][A-ZА-ЯЁ0-9]{1,4})?|пример\s+условного.*)$', re.IGNORECASE)


def _classify_sheet_type(page_text: str, page_num: int) -> str:
    """Барьер 1: Классификация типа листа РД (Спецификация/ВОР vs Общие данные vs Чертёж)."""
    low = (page_text or "").lower()
    if '|' in low or any(k in low for k in (
        'спецификация оборудования', 'ведомость объемов работ', 'ведомость объёмов работ',
        'ведомость материалов', 'кабельный журнал', 'трубный журнал',
        'экспликация помещений', 'ведомостǥ проездов', 'ведомость проездов', 'ведомость бортового камня'
    )):
        return 'SPEC_SHEET'
    if page_num <= 4 and any(k in low for k in ('общие данные', 'ведомость рабочих чертежей', 'ведомость ссылочных')):
        return 'GENERAL_DATA'
    return 'DRAWING_SHEET'

def _normalize_dedup_signature(name: str) -> str:
    """Барьер 3: Сигнатура материала для устранения дублей между листами одного тома."""
    s = re.sub(r'\s*\([^\)]*\)\s*', ' ', (name or "").lower())
    s = re.sub(r'^(?:прокладка\s+кл\s+[\d,\.]+\s*кв\s+|кабель\s+силовой\s+|кабель\s+|труба\s+)', '', s)
    s = re.sub(r'\s+всего:.*$', '', s)
    s = re.sub(r'[^a-zа-яё0-9]+', '', s)
    return s[:60]


TWO_NUMS_RE = re.compile(
    r'^(\d+(?:[\.,]\d+)?)\s+(\d+(?:[\.,]\d+)?)\s*(м2|м²|м3|м³)\b',
    re.IGNORECASE
)
ROOM_RE = re.compile(
    r'((?:Серверная|Тех\.\s*кабинет|Коридор|Кроссовая|Щитовая|Электрощитовая|Венткамера|Помещение|Офис|Тамбур|Подвал|ИТП)\s*\(?\s*пом\.?\s*[А-ЯЁ0-9\.\-]+\s*\)?|\bпом\.?\s*[А-ЯЁ0-9\.\-]+)',
    re.IGNORECASE
)
CABINET_RE = re.compile(
    r'((?:Шкаф|Щит|Панель|Стойка|Узел)\s+[А-ЯЁA-Z0-9\.\-\s]{1,25}?)(?=[А-ЯЁA-Z][а-яёa-z]|$|\|)',
    re.IGNORECASE
)
FLOOR_RE = re.compile(
    r'((?:Подвал|Цоколь|[+-]?\d+[\.,]\d{3}|[1-9]\d?\s*этаж|эт\.\s*[+-]?\d+))',
    re.IGNORECASE
)
THICKNESS_RE = re.compile(r'(\d+\s*мм)', re.IGNORECASE)

TEP_KEYWORDS = (
    # Общие итоги и показатели (ТЭП)
    'объем', 'объём', 'площадь', 'строительный', 'общий итог', 'итого по', 'всего по',
    # Земляные работы и синонимы (ГП, КЖ0.1, ННС)
    'выемка', 'отрывка', 'добор грунта', 'разработка грунта', 'засыпка', 'обратная засыпка',
    'срезка', 'планировка', 'котлован', 'траншея', 'уплотнение', 'трамбован',
    # Дороги, благоустройство и покрытия (01-ГП)
    'проезд', 'тротуар', 'дорожк', 'покрыти', 'отмостк', 'бортов', 'поребрик',
    'газон', 'озеленен', 'асфальтобетон', 'плитка тротуар', 'щебеночн', 'песчан',
    # Конструктив, монтаж и отделка (КЖ, АР, АИ, Инженерные сети)
    'бетонирован', 'армирован', 'гидроизоляц', 'утеплен', 'стяжк', 'штукатур',
    'окраск', 'облицовк', 'монтаж', 'прокладк', 'испытан', 'пусконаладк'
)

LIMIT_KEYWORDS = ('допустимая нагрузка', 'нагрузка на', 'огнестойкост', 'опасности км', 'предел')

LEGEND_KEYWORDS = (
    'условные обозначения', 'условное обозначение', 'экспликация условных',
    'граница участка', 'граница проектирования', 'ось трассы', 'существующие сети',
    'проектируемые сети', 'масштаб', 'формат а'
    'примечания:', 'примечание:', 'система координат', 'система высот',
    'горизонтали проведены', 'граница земельного участка', 'земельный участок',
    'гпзу', 'r20', 's1=', 's3=',
    'примечания', 'примечание', 'зу-1', 'зу-2', 'гпзу',
)
TABLE_HEADER_KEYWORDS = (
    'ведомость', 'спецификация', 'экспликация', 'экспликация помещений',
    'планировка', 'экспликация пола', 'ведомость отделки',
    'ведомость объемов работ', 'ведомость монтажа', 'лист', 'лист 1',
    'наименование и техническая характеристика', 'ед. изм.', 'ед.изм.',
    'единица измерения', 'кол-во', 'кол.', 'количество', 'масса', 'вес',
    'примечания', 'таблица', 'марка', 'обозн.', 'формат', 'фаза', 'стадия',
    'шифр', 'разраб.', 'проверил', 'руковод.', 'н.контроль', 'гип', 'гап',
    '№п. п', '№ п.п', 'h, м', 's, м²', 'v, м³', 'тип обозн.', 'ведомостǥ',
)

TOTALS_KEYWORDS = (
    # Табличные итоги и суммы (отсекаем, чтобы не удваивать закупку)
    'итого', 'всего', 'всего по', 'итого по', 'общий итог',
    'итого по проекту', 'итог по объекту', 'итого по разделу',
    'всего по разделу', 'всего по спецификации', 'итого по ведомости',
    'итого по листу', 'итого по этажу', 'итого по корпусу',
    # Вложенные расшифровки (включая сокращения ГОСТ)
    'в том числе', 'всего в том числе', 'в т.ч.', 'в т. ч.',
    # Итоговые веса и длины (для разделов КЖ, КМ, ЭС, СКС)
    'сумма', 'общая масса', 'масса итого', 'всего масса', 'общая длина',
)

REF_SKIP_PREFIXES = (
    'см.', 'см ', 'листам', 'листа', 'черт.', 'чертежу',
    'по чертежу', 'спец. прим.', 'примечание', 'актов. №',
)

REF_NODE_MARKERS = (
    'серия', 'типовой проект', 'по серии', 'тип. узел',
    'типовой узел', 'узел', 'деталь', 'деталь №', 'поз.',
)

NETWORKS_DRAWING_LABELS = (
    'условная горизонталь', 'масштаб', 'м 1:', 'м 1:50', 'м 1:100',
    'м 1:200', 'м 1:500', 'разрез', 'фасад', 'план на отм.',
    'план на отметке', 'аксонометрия', 'однолинейная схема', 'принципиальная схема',
)

TABLE_UNIT_FIRST_RE = re.compile(rf'^([^|]+?)\s*\|\s*({UNITS})\s*\|\s*(\d+(?:[\.,]\d+)?)\s*$', re.IGNORECASE)
TABLE_QTY_FIRST_RE = re.compile(rf'^([^|]+?)\s*\|\s*(\d+(?:[\.,]\d+)?)\s*\|\s*({UNITS})\s*$', re.IGNORECASE)
PLAIN_TEXT_RE = re.compile(rf'^(.{{4,140}}?)\s*[-–—]?\s*(\d+(?:[\.,]\d+)?)\s*({UNITS})(?![а-яёa-z0-9²³])', re.IGNORECASE)


def _is_corrupted_cad_font(text: str) -> bool:
    """Отсекает только полностью нечитаемый SHX-мусор, пропуская строки с единичными заменами букв."""
    if not text:
        return True
    garbage_chars = set("ЗћЗјЗ¶З№З­ЗёИ†З°З¬ЗІЗ«И‚ЗіИЉЗµЗ±З·З»ЗѕЗєЗ–З•¶ѕ±¬°")
    bad_count = sum(1 for ch in text if ch in garbage_chars and ch not in "ЗИ")
    # Отсекаем только если больше трети строки состоит из битых символов
    return bad_count >= max(4, len(text) // 3)


def _detect_discipline(doc_title: str) -> str:
    upper = (doc_title or "").upper()
    for code in ('СКС', 'АР', 'АИ', 'КЖ', 'КМ', 'ГП', 'ОВ', 'ВК', 'ЭС', 'ЗКВС', 'ННС'):
        if code in upper:
            return code
    return "РД"


def _infer_room_materials_and_brigade(room_label: str, discipline: str) -> tuple[str, str]:
    """Подбирает типовой пирог материалов и профильную бригаду под назначение помещения."""
    low = (room_label or "").lower()
    if "итп" in low or "насос" in low or "подвал" in low:
        return (
            "Бетон B7.5 / гидроизоляция, керамогранит тех., влагостойкая окраска",
            "Звено №2 (Бетонщики / Отделочники-гидроизолировщики)",
        )
    if "сервер" in low or "кросс" in low or "тех. кабинет" in low:
        return (
            "Антистатический фальшпол, лотки, кабель СКС, шкафы 19\"",
            "Звено №4 (Слаботочники СКС / АСУ ТП)",
        )
    if "щитов" in low or "вру" in low:
        return (
            "Кабель ВВГнг-LS, лотки перфорированные, контур заземления, щиты",
            "Звено №3 (Электромонтажники ЭС)",
        )
    if "венткамер" in low:
        return (
            "Воздуховоды оцинкованные, огнезадерживающие клапаны, виброопоры",
            "Звено №5 (Монтажники ОВ и вентиляции)",
        )
    decoded = resolve_section_and_brigade(discipline)
    return (
        "Материалы и изделия по ведомости раздела РД",
        decoded.get("brigade") or "Звено ПТО (Общестрой)",
    )


def _classify_tmc_group(material_name: str, discipline: str) -> str:
    """Распределяет позицию по 7 методическим группам ТМЦ склада и снабжения."""
    low = (material_name or "").lower()
    if any(k in low for k in ("бетон", "песок", "щебень", "грунт", "раствор", "цемент")):
        return "01. Инертные, Грунт и Бетон"
    if any(k in low for k in ("арматур", "анкер", "металл", "швеллер", "кольцо кс", "плита пп", "днище")):
        return "02. Металл, Крепёж и ЖБИ"
    if any(k in low for k in ("плит", "керамогранит", "вата", "барьер", "краск", "штукатур", "фальшпол", "отделк", "площадь")):
        return "03. Отделка и Изоляция"
    if any(k in low for k in ("коммутатор", "патч", "органайзер", "шкаф тш", "кабель", "витая", "оптик")) or discipline == "СКС":
        return "04. Кабель и Оборудование СКС"
    if any(k in low for k in ("щит", "автомат", "вру", "светильник", "заземлен")) or discipline == "ЭС":
        return "05. Электромонтаж и Щиты"
    if any(k in low for k in ("труб", "воздуховод", "клапан", "насос", "вентилятор")) or discipline in ("ОВ", "ВК", "ННС"):
        return "06. Инженерные сети (ОВ / ВК / ННС)"
    return "07. Общестроительные ТМЦ"


def parse_specifications_and_create_requests(doc, staff_label: str = "ПТО Штаб") -> dict:
    """Точка входа релейного конвейера для разбора ведомостей и помещений."""
    warehouse_items = list(WarehouseTmc.objects.all())
    discipline = _detect_discipline(doc.title)
    return _run_spec_pipeline(doc, staff_label, warehouse_items, discipline)


def _run_spec_pipeline(doc, staff_label: str, warehouse_items: list, discipline: str) -> dict:
    aggregated = {}
    spec_sheet_signatures = set()
    current_floor = ""
    current_room = ""
    last_line_item_label = ""
    active_pavement_area = Decimal("0")
    pending_pave_header = False
    pending_layer_name = ""

    pages_list = list(doc.pages.all().order_by('page_number'))
    classified_pages = [(p, _classify_sheet_type(p.text or "", p.page_number)) for p in pages_list]
    ordered_pages = sorted(classified_pages, key=lambda pair: 0 if pair[1] == 'SPEC_SHEET' else 1)

    for page, sheet_type in ordered_pages:
        if not page.text or sheet_type == 'GENERAL_DATA':
            continue

        page_text = page.text
        # Лечим разрывы марок кабелей и единиц в AutoCAD ("Пв | БШвнг" -> "ПвБШвнг", "0,4к | В" -> "0,4кВ")
        page_text = re.sub(r'(А?Пв)\s*\|\s*(БШв)', r'\1\2', page_text, flags=re.IGNORECASE)

        page_text = re.sub(r'(\d)\s*к\s*\|\s*В\b', r'\1 кВ', page_text)
        # Разрезаем слипшиеся выноски труб ("L = 1х11м1 тр. ПЭ" -> "L = 1х11м\n1 тр. ПЭ")
        page_text = re.sub(r'(\d+\s*м)(\d+\s*тр\.)', r'\1\n\2', page_text, flags=re.IGNORECASE)
        # Отсекаем масштаб чертежа ("М 1:500"), чтобы 500 не попадало в длину кабеля
        page_text = re.sub(r'\bМ\s*1\s*:\s*\d+\b', '', page_text)
        # Отсекаем пустые шапки таблиц объёмов грунта
        page_text = re.sub(r'^.*Наименование\s+работ\s+и\s+объемов\s+грунта.*$', '', page_text, flags=re.MULTILINE | re.IGNORECASE)


        # Лечим разрывы мощности и расхода в ИТП/ОВ ("0,37к | Вт" -> "0,37 кВт", "м3/ч" сохраняем)
        page_text = re.sub(r'(\d)\s*к\s*\|\s*Вт\b', r'\1 кВт', page_text, flags=re.IGNORECASE)
        # Разрезаем прилипшие номера позиций спецификации ("3.4Клапан" -> "\n3.4 Клапан", "шт13.5Фильтр" -> "шт 1\n3.5 Фильтр")
        page_text = re.sub(r'(?<=[а-яёa-z0-9\.\)])(\d{1,2}\.\d{1,2}(?:\.\d{1,2})?)([А-ЯЁA-Z])', r'\n\1 \2', page_text)
        # Отделяем прилипшую единицу и кол-во от завода ("Риданшт2 25,8" -> "Ридан — 2 шт")
        page_text = re.sub(
            r'([А-ЯЁA-Za-zа-яё]{2,})(шт\.?|компл\.?|рул\.?|упак\.?)(\d+(?:[\.,]\d+)?)(?:\s+\d+(?:[\.,]\d+)?)?',
            r'\1 — \3 \2',
            page_text
        )

        # Лечим обратную склейку ВОР AutoCAD ("всего:м962" -> "всего: 962 м", "ммм280" -> "мм — 280 м")
        page_text = re.sub(r'(?<![а-яёa-z0-9])м(\d+(?:[\.,]\d+)?)(?![а-яёa-z0-9²³])', r' — \1 м ', page_text)
        page_text = re.sub(r'(мм)м(\d+(?:[\.,]\d+)?)\b', r'\1 — \2 м ', page_text)
        # Отделяем слово "Бордюр" на новую строку, если к нему прилип заголовок таблицы
        page_text = re.sub(r'([^\n])(Бордюр(?:\s+дорожный|\s+садовый|ный\s+камень))', r'\1\n\2', page_text)
        # Разрезаем склейки AutoCAD вида "п.м380.00Бордюрный" -> " — 380.00 м\nБордюрный"
        page_text = re.sub(
            r'(?:п\.?\s*м|м\.?\s*п)\.?\s*(\d+(?:[\.,]\d+)?)([А-ЯЁA-Z])',
            r' — \1 м\n\2',
            page_text
        )
        page_text = re.sub(
            r'(?:п\.?\s*м|м\.?\s*п)\.?\s*(\d+(?:[\.,]\d+)?)\b',
            r' — \1 м',
            page_text
        )

        for raw_line in page_text.split('\n'):
            if _is_corrupted_cad_font(raw_line):
                continue
            stripped = raw_line.strip()
            if len(stripped) < 3:
                continue
            # 1. Отклеиваем прилипшую "L=" от сечения кабеля/диаметра трубы ("5х185L=2x107м" -> "5х185 L=2x107м")
            stripped = re.sub(r'(?<=[0-9А-ЯЁа-яёA-Za-zØø])([Ll]\s*=)', r' \1', stripped)
            # Склеиваем пробелы в целых тысячах ("4 701 м2" -> "4701 м2")
            stripped = re.sub(r'(?<![\.,\d])(\d{1,3})\s+(\d{3})(?=\s*(?:м2|м²|м3|м³|м|шт|кг|т)\b)', r'\1\2', stripped)

            # Шаг 1А: Запоминаем заголовок многострочной выноски (если есть марка кабеля/трубы, но ещё нет метража)
            if (
                re.search(r'(?:ПвБШв|АПвБШв|ВВГ|АВБШв|ППГ|ПНД|ПЭ\s*Ø|тр\.\s*П)', stripped, re.IGNORECASE)
                and not re.search(r'\d+(?:[\.,]\d+)?\s*(?:м|шт|кг|т)(?![а-яёa-z0-9²³])', stripped, re.IGNORECASE)
            ):
                last_line_item_label = stripped.replace('L=', '').strip()
                continue

            # Шаг 1Б: Если строка начинается с длины "L=..." (напр. "L=2x107м (ввод 2)"), приклеиваем к запомненной марке ДО расчёта множителей
            if last_line_item_label and re.match(r'^(?:[Ll]\s*=\s*)?\d+(?:[\.,]\d+)?\s*(?:[xх×\*]\s*\d+(?:[\.,]\d+)?)?\s*м\b', stripped, re.IGNORECASE):
                stripped = f"{last_line_item_label} {stripped}"

            # Шаг 1В: Проверяем количество кабелей в пучке в начале строки ("2 АПвБШв..." или "4 АПвБШв...")
            m_bundle = re.match(r'^(\d{1,2})\s+((?:ПвБШв|АПвБШв|ВВГ|АВБШв|ППГ|КГВВ|МКЭШ).+)$', stripped, flags=re.IGNORECASE)
            bundle_count = int(m_bundle.group(1)) if m_bundle else 1
            if m_bundle:
                stripped = m_bundle.group(2).strip()

            # Если внутри L= уже стоит множитель (L=2x107м) — берём его напрямую без двойного умножения на bundle_count
            if re.search(r'[Ll]\s*=\s*\d+\s*[xх×\*]\s*\d', stripped):
                stripped = re.sub(
                    r'[Ll]\s*=\s*(\d+)\s*[xх×\*]\s*(\d+(?:[\.,]\d+)?)\s*(м)(?![а-яёa-z0-9²³])',
                    lambda m: f"L={float(m.group(1)) * float(m.group(2).replace(',', '.')):g} {m.group(3)}",
                    stripped
                )
            else:
                # Если внутри L= множителя нет ("2 АПвБШв... L=143м") — умножаем на число кабелей в пучке bundle_count
                stripped = re.sub(
                    r'[Ll]\s*=\s*(\d+(?:[\.,]\d+)?)\s*(м)(?![а-яёa-z0-9²³])',
                    lambda m: f"L={bundle_count * float(m.group(1).replace(',', '.')):g} {m.group(2)}",
                    stripped
                )


            # 2. Ловим строки «Ведомости проездов, тротуаров, дорожек» (Наименование + h,м + S,м² + V,м³)
            hsv_early = re.match(
                r'^(?:\d{1,2}[\.\)]?\s+)?((?:Проезд|Тротуар|Дорожка|Отмостка|Площадка|Покрытие|Асфальтобетон|Плитка|Бордюр)[^0-9]{2,95}?)\s+(\d+[\.,]\d{1,3})\s+(\d+(?:\s?\d{3})*(?:[\.,]\d{1,3})?)\s+(\d+(?:\s?\d{3})*(?:[\.,]\d{1,3})?)(?:\s+(.*))?$',
                stripped,
                flags=re.IGNORECASE
            )
            if hsv_early:
                road_name = hsv_early.group(1).strip()
                h_val = hsv_early.group(2).replace(',', '.')
                s_clean = hsv_early.group(3).replace(' ', '').replace(',', '.')
                v_clean = hsv_early.group(4).replace(' ', '').replace(',', '.')
                road_type = (hsv_early.group(5) or "").strip()
                stripped = f"{road_name} [h={h_val}, V={v_clean} {road_type}] — {s_clean} м2"


                        # 3. Ловим заголовок дорожной одежды ("Конструкция проездов/тротуаров/отмостки")
            if re.search(r'Конструкция\s+(?:проездов|тротуаров|отмостки|площадок)', stripped, flags=re.IGNORECASE):
                pending_pave_header = True
                m_same_line = re.search(r'\b0[\.,]\d{2}\s+(\d+(?:\s?\d{3})*(?:[\.,]\d{1,3})?)\s+\d+(?:\s?\d{3})*(?:[\.,]\d{1,3})?', stripped)
                if m_same_line:
                    active_pavement_area = Decimal(m_same_line.group(1).replace(' ', '').replace(',', '.'))
                    pending_pave_header = False
                continue

            if pending_pave_header:
                m_next_area = re.search(r'\b0[\.,]\d{2}\s+(\d+(?:\s?\d{3})*(?:[\.,]\d{1,3})?)\s+\d+(?:\s?\d{3})*(?:[\.,]\d{1,3})?', stripped)
                if m_next_area:
                    active_pavement_area = Decimal(m_next_area.group(1).replace(' ', '').replace(',', '.'))
                    pending_pave_header = False
                    continue

            if active_pavement_area > 0:
                if 'геосинтетический материал' in stripped.lower():
                    stripped = f"Геосинтетический материал 300 г/м2 — {active_pavement_area} м2"
                    pending_layer_name = ""
                elif re.match(r'^0[\.,]\d{2}$', stripped) and pending_layer_name:
                    h_layer = Decimal(stripped.replace(',', '.'))
                    if any(w in pending_layer_name.lower() for w in ('брусчат', 'плитк')):
                        stripped = f"{pending_layer_name} — {active_pavement_area} м2"
                    else:
                        vol_m3 = (active_pavement_area * h_layer).quantize(Decimal("0.01"))
                        stripped = f"{pending_layer_name} [h={h_layer}] — {vol_m3} м3"
                    pending_layer_name = ""
                elif any(w in stripped.lower() for w in ('брусчат', 'тротуарная плитка', 'щебен', 'щебн', 'песок', 'асфальтобетон', 'цементнопесчан', 'цементно-песчан', 'бетон')):
                    m_inline_h = re.search(r'^(.*?)\s+(0[\.,]\d{2})$', stripped)
                    if m_inline_h:
                        l_name = m_inline_h.group(1).lstrip('- ').strip()
                        h_layer = Decimal(m_inline_h.group(2).replace(',', '.'))
                        if any(w in l_name.lower() for w in ('брусчат', 'плитк')):
                            stripped = f"{l_name} — {active_pavement_area} м2"
                        else:
                            vol_m3 = (active_pavement_area * h_layer).quantize(Decimal("0.01"))
                            stripped = f"{l_name} [h={h_layer}] — {vol_m3} м3"
                        pending_layer_name = ""
                    else:
                        pending_layer_name = stripped.lstrip('- ').strip()
                        continue

            m_floor = FLOOR_RE.search(stripped)
            if m_floor and len(stripped) < 60:
                current_floor = m_floor.group(1).strip()

            m_rh = ROOM_HEADER_RE.match(stripped)
            if m_rh:
                current_room = f"Пом. {m_rh.group(1)} — {m_rh.group(2).strip()}"
                continue

            m_two = TWO_NUMS_RE.match(stripped)

            if m_two:
                floor_area = Decimal(m_two.group(1).replace(',', '.'))
                wall_area = Decimal(m_two.group(2).replace(',', '.'))
                unit_val = m_two.group(3)
                room_label = current_room or "Помещение по экспликации"
                mat_hint, brigade_name = _infer_room_materials_and_brigade(room_label, discipline)
                tmc_grp = _classify_tmc_group(mat_hint, discipline)
                shifts = max(1, int(((floor_area + wall_area) / Decimal("65")).to_integral_value()))

                summary_title = (
                    f"{room_label} → Площадь пола: {floor_area} {unit_val} | "
                    f"Площадь отделки / объём: {wall_area} {unit_val}"
                )
                k = ('tep', room_label.lower(), room_label.lower(), "")
                aggregated[k] = {
                    'record_type': 'TEP',
                    'discipline': discipline,
                    'floor_info': current_floor[:60],
                    'room_info': room_label[:120],
                    'node_cabinet': f"[{tmc_grp}] {mat_hint}"[:120],
                    'material': summary_title[:255],
                    'unit': unit_val,
                    'required': floor_area + wall_area,
                    'brigade': brigade_name[:120],
                    'schedule_hint': f"~{shifts} см. (По графику ГПР)",
                    'notes': f"ОЖР-заготовка: {room_label} | {tmc_grp} | Границы: пол и перекрытие ({doc.title})"[:255],
                }
                continue

            line = re.sub(r'^\d{1,3}[\.\)]?\s+(?=[А-ЯЁA-Z])', '', stripped)
            name, unit, qty_str = None, None, None
            for rx, order in ((TABLE_UNIT_FIRST_RE, 'u_q'), (TABLE_QTY_FIRST_RE, 'q_u'), (PLAIN_TEXT_RE, 'q_u')):
                m = rx.match(line)
                if m:
                    if order == 'u_q':
                        name, unit, qty_str = m.group(1), m.group(2), m.group(3)
                    else:
                        name, qty_str, unit = m.group(1), m.group(2), m.group(3)
                    break

            if not name or not qty_str or not unit:
                continue

            room_found = current_room
            cabinet_found = ""
            clean_name = name.strip()

            m_r = ROOM_RE.search(clean_name)
            if m_r:
                room_found = m_r.group(1).strip()
                clean_name = clean_name.replace(m_r.group(0), " ").strip()

            m_c = CABINET_RE.search(clean_name)
            if m_c:
                cabinet_found = m_c.group(1).strip()
                clean_name = clean_name.replace(m_c.group(0), " ").strip()

            m_th = THICKNESS_RE.search(clean_name)
            if m_th and not cabinet_found and discipline in ('АР', 'АИ'):
                cabinet_found = f"Слой {m_th.group(1)}"

            clean_name = re.sub(r'^[\-\–\—\)\(\s]+|[\-\–\—\s]+$', '', clean_name)
            clean_name = re.sub(r'\s+', ' ', clean_name).strip()

            if len(clean_name) < 4 or re.match(r'^[\d\s\.,\-/]+$', clean_name):
                continue

            _, brigade_name = _infer_room_materials_and_brigade(room_found or clean_name, discipline)
            tmc_grp = _classify_tmc_group(clean_name, discipline)
            qty = Decimal(qty_str.replace(',', '.'))

            hsv_match = re.match(
                r'^(?:\d{1,2}\s+)?([А-ЯЁA-Z][^0-9]{4,90}?)\s+(\d+[\.,]\d{1,3})\s+(\d+[\.,]\d{1,3})\s+(\d+[\.,]\d{1,3})(?:\s+(.*))?$',
                stripped
            )
            if hsv_match:
                road_name = hsv_match.group(1).strip()
                h_val = hsv_match.group(2).replace(',', '.')
                s_val = Decimal(hsv_match.group(3).replace(',', '.'))
                v_val = hsv_match.group(4).replace(',', '.')
                road_type = (hsv_match.group(5) or "").strip()
                clean_name = f"{road_name} (h={h_val} м, V={v_val} м³ {road_type})".strip()
                qty = s_val
                unit = "м2"

            shifts = max(1, int((qty / Decimal("120")).to_integral_value()))

            # Перехват поставщиков/заводов из чертежей для партнёрской программы (до очистки e-mail)

            clean_name = re.sub(r',?\s*"[^"]+",?\s*E-?mail:\s*\S+', '', clean_name, flags=re.IGNORECASE).strip()
            clean_name = re.sub(r'\s*E-?mail:\s*\S+', '', clean_name, flags=re.IGNORECASE).strip()

            lower_name = clean_name.lower()


            if (
                lower_name in TABLE_HEADER_KEYWORDS
                or any(lower_name.startswith(h + ' ') for h in ('ведомость', 'спецификация', 'экспликация', 'таблица'))
                or any(k in lower_name for k in LEGEND_KEYWORDS)
                or any(lower_name.startswith(t) or f' {t}' in lower_name for t in TOTALS_KEYWORDS)
                or any(lower_name.startswith(pref) for pref in REF_SKIP_PREFIXES)
                or any(lower_name.startswith(lbl) for lbl in NETWORKS_DRAWING_LABELS)

            ):
                continue

            DEMOLITION_KEYWORDS = (
                'демонтаж', 'демонтируем', 'демонтировать', 'дем.',
                'разборка', 'разбор ', 'разобрать', 'разбивка', 'разломка', 'слом ',
                'снос ', 'снести', 'ликвидация', 'ликвидируем',
                'срезка', 'снятие растительного', 'снятие плодородного', 'снятие слоя',
                'фрезерование', 'кирковка', 'вскрытие покрытия', 'вскрытие асфальт',
                'корчевка', 'корчёвка', 'валка деревьев', 'вырубка', 'расчистка территории',
                'разработка грунта', 'обратная засыпка', 'планировка площади', 'уплотнение грунта',
                'пробивка отверстий', 'пробивка проемов', 'пробивка проёмов',
                'алмазное бурение', 'алмазная резка', 'резка швов', 'штробление', 'бороздение',
                'очистка поверхности', 'пескоструйная', 'дробеструйная', 'отбивка штукатурки',
                'вывоз мусора', 'вывоз грунта', 'вывоз строительного', 'погрузка мусора',
                'утилизация', 'бой бетона', 'бой кирпича', 'скол бетона',
                'отключение существующ', 'заглушка существующ', 'переключение существующ',
                'удаление существующ', 'существующий бортовой', 'существующего бортового',
            )
            if any(k in lower_name for k in TEP_KEYWORDS) or any(k in lower_name for k in DEMOLITION_KEYWORDS):
                rec_type = 'TEP'
            elif any(k in lower_name for k in LIMIT_KEYWORDS):
                rec_type = 'LIMIT'
            else:
                rec_type = 'BUY'

            node_label = f"[{tmc_grp}] {cabinet_found}".strip()
            note_txt = f"ОЖР-заготовка: {tmc_grp} | Том {doc.title} (Рев. {doc.revision_num})"

            agg_key = (rec_type, lower_name, room_found.lower(), node_label.lower())
            if agg_key not in aggregated:
                aggregated[agg_key] = {
                    'record_type': rec_type,
                    'discipline': discipline,
                    'floor_info': current_floor[:60],
                    'room_info': room_found[:120],
                    'node_cabinet': node_label[:120],
                    'material': clean_name[:255],
                    'unit': unit.strip(),
                    'required': Decimal('0'),
                    'brigade': brigade_name[:120],
                    'schedule_hint': f"~{shifts} см.",
                    'notes': note_txt[:255],
                }
            aggregated[agg_key]['required'] += qty

    PurchaseRequest.objects.filter(document=doc, status='NEW').delete()
    created_buy, created_tep, created_limit, in_stock_covered = 0, 0, 0, 0

    for item in aggregated.values():
        if item['record_type'] == 'BUY':
            stock_match = next(
                (w for w in warehouse_items if w.nomenclature.lower() in item['material'].lower()
                 or item['material'].lower() in w.nomenclature.lower()),
                None
            )
            in_stock = stock_match.stock_balance if stock_match else Decimal('0')
            deficit = max(Decimal('0'), item['required'] - in_stock)
            if deficit > 0:
                PurchaseRequest.objects.create(
                    document=doc, record_type='BUY', discipline=item['discipline'],
                    floor_info=item['floor_info'], room_info=item['room_info'],
                    node_cabinet=item['node_cabinet'], material_name=item['material'],
                    unit=item['unit'], required_qty=item['required'], deficit_qty=deficit,
                    brigade_assigned=item['brigade'], schedule_hint=item['schedule_hint'],
                    responsible_itr=staff_label[:120], status='NEW', notes=item['notes'],
                )
                created_buy += 1
            else:
                in_stock_covered += 1
        else:
            PurchaseRequest.objects.create(
                document=doc, record_type=item['record_type'], discipline=item['discipline'],
                floor_info=item['floor_info'], room_info=item['room_info'],
                node_cabinet=item['node_cabinet'], material_name=item['material'],
                unit=item['unit'], required_qty=item['required'], deficit_qty=Decimal('0'),
                brigade_assigned=item['brigade'], schedule_hint=item['schedule_hint'],
                responsible_itr=staff_label[:120], status='NEW', notes=item['notes'],
            )
            if item['record_type'] == 'TEP':
                created_tep += 1
            else:
                created_limit += 1

    return {
        "total_positions": len(aggregated),
        "requests_created": created_buy,
        "tep_created": created_tep,
        "limits_created": created_limit,
        "covered_by_stock": in_stock_covered,
    }
