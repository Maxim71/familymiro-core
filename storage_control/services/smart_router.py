# -*- coding: utf-8 -*-
import re

DOCUMENT_PROFILES = {
    "FINISH_AR": {
        "name": "Архитектурные решения и ведомости отделки (АР)",
        "section": "АР",
        "keywords": (
            "ведомость отделки", "отделк", "помещен", "потолок", "плинтус",
            "перегород", "экспликация", "полов", "заполнение проемов", "ар0", "-ар",
        ),
        "noise_patterns": (
            r'типотделки',
            r'[\u4e00-\u9fff]{2,}',
            r'^№\s*помещен',
            r'^наименование\s+помещен',
            r'^тип\s+потолка',
            r'^примечание\s*$',
        ),
        "expected_units": ("м2", "м²", "м", "пог. м", "шт"),
    },
    "METAL_KZH": {
        "name": "Конструкции железобетонные и металлические (КЖ / КМ)",
        "section": "КЖ",
        "keywords": (
            "-кж", "-км", "кж.", "км.", "армирован", "ведомость расхода стали",
            "спецификация арматуры", "фундамент", "монолитн", "перекрыт", "колонн",
        ),
        "noise_patterns": (
            r'^\d{6,}[а-яёa-z]{1,3}\d*',
            r'^деталь\s+\d+',
            r'^ведомость\s+деталей',
            r'^позиция\s+эскиз',
            r'^масса\s+детали',
            r'^итого\s+по\s+марке',
        ),
        "expected_units": ("кг", "т", "м3", "м³", "шт", "м"),
    },
    "POWER_ES": {
        "name": "Электроснабжение, силовые сети и щиты (ЭС / ЭО / ЭМ / ЭГ)",
        "section": "ЭС",
        "keywords": (
            "-эс", "-эо", "-эм", "-эг", "эс.", "кабельный журнал",
            "однолинейная", "вру", "грщ", "щит", "заземлен", "молниезащит",
        ),
        "noise_patterns": (
            r'^расчетный\s+ток',
            r'^потеря\s+напряжения',
            r'^условное\s+обозначение',
            r'^номер\s+группы',
            r'^маркировка\s+кабеля',
        ),
        "expected_units": ("м", "пог. м", "шт", "компл", "кг"),
    },
    "FIRE_SECURITY_SPA": {
        "name": "Пожарная автоматика, СПА, АПС, СС и АСУ ТП (СПА / СС / АК)",
        "section": "СПА",
        "keywords": (
            "-спа", "-апс", "-сс", "-ак", "-асутп", "спа.", "пожарн",
            "сириус", "ппку", "извещател", "оповещател", "скуд", "видеонаблюден",
        ),
        "noise_patterns": (
            r'^шлейф\s+сигнализации',
            r'^адрес\s+устройства',
            r'^условное\s+обозначение',
            r'^ток\s+потребления',
        ),
        "expected_units": ("шт", "компл", "м", "пог. м"),
    },
    "HVAC_OV_VK": {
        "name": "Отопление, вентиляция, кондиционирование, ВК и ИТП (ОВ / ВК / ХС)",
        "section": "ОВ",
        "keywords": (
            "-ов", "-вк", "-хс", "-итп", "ов.", "вк.", "воздуховод",
            "вентиляц", "отоплен", "канализац", "водопровод", "тепловой пункт", "холодоснабж",
        ),
        "noise_patterns": (
            r'^характеристика\s+отопительно',
            r'^аэродинамический\s+расчет',
            r'^скорость\s+воздуха',
            r'^потери\s+давления',
        ),
        "expected_units": ("м", "пог. м", "м2", "м²", "шт", "компл", "кг"),
    },
    "CIVIL_GP": {
        "name": "Генеральный план, наружные сети и благоустройство (ГП / НВК / АД)",
        "section": "ГП",
        "keywords": (
            "-гп", "-нвк", "-ад", "гп.", "благоустройств", "бордюр",
            "покрыт", "озеленен", "земляных масс", "наружн", "ливнев",
        ),
        "noise_patterns": (
            r'^ведомость\s+объемов\s+земляных',
            r'^условные\s+обозначения',
            r'^отметка\s+земли',
        ),
        "expected_units": ("м2", "м²", "м3", "м³", "м", "пог. м", "шт", "т"),
    },
    "TECH_COD": {
        "name": "Технологические решения и стойки ЦОД (ТХ)",
        "section": "ТХ",
        "keywords": ("-тх", "тх.", "стойк", "серверн", "цод", "технологическ", "фальшпол"),
        "noise_patterns": (
            r'^тепловыделение\s+стойки',
            r'^условное\s+обозначение',
        ),
        "expected_units": ("шт", "компл", "м2", "м²", "м"),
    },
    "GENERAL_RD": {
        "name": "Общая рабочая документация (ГОСТ 21.110-2013)",
        "section": "РД",
        "keywords": (),
        "noise_patterns": (),
        "expected_units": ("шт", "компл", "м", "м2", "м3", "кг", "т"),
    },
}


def detect_document_profile(doc_title: str, sample_text: str = "") -> dict:
    """Определяет строительный профиль любого из 76 томов по шифру файла и тексту листов."""
    title_low = (doc_title or "").lower()
    for code, cfg in DOCUMENT_PROFILES.items():
        if code == "GENERAL_RD":
            continue
        if any(kw in title_low for kw in cfg["keywords"]):
            return {"code": code, **cfg}

    text_low = (sample_text[:2500] or "").lower()
    best_code = "GENERAL_RD"
    best_hits = 0
    for code, cfg in DOCUMENT_PROFILES.items():
        if code == "GENERAL_RD":
            continue
        hits = sum(1 for kw in cfg["keywords"] if kw in text_low)
        if hits > best_hits:
            best_hits = hits
            best_code = code

    return {"code": best_code, **DOCUMENT_PROFILES[best_code]}


def is_noise_for_document(doc_title: str, row_text: str) -> bool:
    """Отсекает технические шапки, расчётные таблицы и AutoCAD/двуязычный шум для профиля тома."""
    raw = (row_text or "").strip()
    low = raw.lower()
    if not low or len(low) < 4:
        return True

    if re.fullmatch(r'[\d\s\.,\-/]+', low):
        return True

    profile = detect_document_profile(doc_title)
    for pat in profile.get("noise_patterns", ()):
        if re.search(pat, low, re.IGNORECASE):
            return True
    return False


def evaluate_parsing_quality(doc_title: str, rows: list[str]) -> dict:
    """Оценивает чистоту и полноту распознавания строк для выбранного профиля РД."""
    profile = detect_document_profile(doc_title)
    clean_cnt = 0
    dropped_cnt = 0
    for r in rows:
        if is_noise_for_document(doc_title, r):
            dropped_cnt += 1
        else:
            clean_cnt += 1
    total = len(rows)
    score_pct = round((clean_cnt / total) * 100, 1) if total else 100.0
    return {
        "profile_code": profile["code"],
        "profile_name": profile["name"],
        "section": profile["section"],
        "total": total,
        "clean": clean_cnt,
        "dropped": dropped_cnt,
        "quality_pct": score_pct,
    }
DOCUMENT_PROFILES = {
    "FINISH_AR": {
        "name": "Архитектурные решения и ведомости отделки (АР)",
        "section": "АР",
        "keywords": (
            "ведомость отделки", "отделк", "помещен", "потолок", "плинтус",
            "перегород", "экспликация", "полов", "заполнение проемов", "ар0", "-ар",
        ),
        "noise_patterns": (
            r'типотделки',
            r'[\u4e00-\u9fff]{2,}',
            r'^№\s*помещен',
            r'^наименование\s+помещен',
            r'^тип\s+потолка',
            r'^примечание\s*$',
        ),
        "expected_units": ("м2", "м²", "м", "пог. м", "шт"),
    },
    "METAL_KZH": {
        "name": "Конструкции железобетонные и металлические (КЖ / КМ)",
        "section": "КЖ",
        "keywords": (
            "-кж", "-км", "кж.", "км.", "армирован", "ведомость расхода стали",
            "спецификация арматуры", "фундамент", "монолитн", "перекрыт", "колонн",
        ),
        "noise_patterns": (
            r'^\d{6,}[а-яёa-z]{1,3}\d*',
            r'^деталь\s+\d+',
            r'^ведомость\s+деталей',
            r'^позиция\s+эскиз',
            r'^масса\s+детали',
            r'^итого\s+по\s+марке',
        ),
        "expected_units": ("кг", "т", "м3", "м³", "шт", "м"),
    },
    "POWER_ES": {
        "name": "Электроснабжение, силовые сети и щиты (ЭС / ЭО / ЭМ / ЭГ)",
        "section": "ЭС",
        "keywords": (
            "-эс", "-эо", "-эм", "-эг", "эс.", "кабельный журнал",
            "однолинейная", "вру", "грщ", "щит", "заземлен", "молниезащит",
        ),
        "noise_patterns": (
            r'^расчетный\s+ток',
            r'^потеря\s+напряжения',
            r'^условное\s+обозначение',
            r'^номер\s+группы',
            r'^маркировка\s+кабеля',
        ),
        "expected_units": ("м", "пог. м", "шт", "компл", "кг"),
    },
    "FIRE_SECURITY_SPA": {
        "name": "Пожарная автоматика, СПА, АПС, СС и АСУ ТП (СПА / СС / АК)",
        "section": "СПА",
        "keywords": (
            "-спа", "-апс", "-сс", "-ак", "-асутп", "спа.", "пожарн",
            "сириус", "ппку", "извещател", "оповещател", "скуд", "видеонаблюден",
        ),
        "noise_patterns": (
            r'^шлейф\s+сигнализации',
            r'^адрес\s+устройства',
            r'^условное\s+обозначение',
            r'^ток\s+потребления',
        ),
        "expected_units": ("шт", "компл", "м", "пог. м"),
    },
    "HVAC_OV_VK": {
        "name": "Отопление, вентиляция, кондиционирование, ВК и ИТП (ОВ / ВК / ХС)",
        "section": "ОВ",
        "keywords": (
            "-ов", "-вк", "-хс", "-итп", "ов.", "вк.", "воздуховод",
            "вентиляц", "отоплен", "канализац", "водопровод", "тепловой пункт", "холодоснабж",
        ),
        "noise_patterns": (
            r'^характеристика\s+отопительно',
            r'^аэродинамический\s+расчет',
            r'^скорость\s+воздуха',
            r'^потери\s+давления',
        ),
        "expected_units": ("м", "пог. м", "м2", "м²", "шт", "компл", "кг"),
    },
    "CIVIL_GP": {
        "name": "Генеральный план, наружные сети и благоустройство (ГП / НВК / АД)",
        "section": "ГП",
        "keywords": (
            "-гп", "-нвк", "-ад", "гп.", "благоустройств", "бордюр",
            "покрыт", "озеленен", "земляных масс", "наружн", "ливнев",
        ),
        "noise_patterns": (
            r'^ведомость\s+объемов\s+земляных',
            r'^условные\s+обозначения',
            r'^отметка\s+земли',
        ),
        "expected_units": ("м2", "м²", "м3", "м³", "м", "пог. м", "шт", "т"),
    },
    "TECH_COD": {
        "name": "Технологические решения и стойки ЦОД (ТХ)",
        "section": "ТХ",
        "keywords": ("-тх", "тх.", "стойк", "серверн", "цод", "технологическ", "фальшпол"),
        "noise_patterns": (
            r'^тепловыделение\s+стойки',
            r'^условное\s+обозначение',
        ),
        "expected_units": ("шт", "компл", "м2", "м²", "м"),
    },
    "GENERAL_RD": {
        "name": "Общая рабочая документация (ГОСТ 21.110-2013)",
        "section": "РД",
        "keywords": (),
        "noise_patterns": (),
        "expected_units": ("шт", "компл", "м", "м2", "м3", "кг", "т"),
    },
}


def detect_document_profile(doc_title: str, sample_text: str = "") -> dict:
    """Определяет строительный профиль любого из 76 томов по шифру файла и тексту листов."""
    title_low = (doc_title or "").lower()
    for code, cfg in DOCUMENT_PROFILES.items():
        if code == "GENERAL_RD":
            continue
        if any(kw in title_low for kw in cfg["keywords"]):
            return {"code": code, **cfg}

    text_low = (sample_text[:2500] or "").lower()
    best_code = "GENERAL_RD"
    best_hits = 0
    for code, cfg in DOCUMENT_PROFILES.items():
        if code == "GENERAL_RD":
            continue
        hits = sum(1 for kw in cfg["keywords"] if kw in text_low)
        if hits > best_hits:
            best_hits = hits
            best_code = code

    return {"code": best_code, **DOCUMENT_PROFILES[best_code]}


def is_noise_for_document(doc_title: str, row_text: str) -> bool:
    """Отсекает технические шапки, расчётные таблицы и AutoCAD/двуязычный шум для профиля тома."""
    raw = (row_text or "").strip()
    low = raw.lower()
    if not low or len(low) < 4:
        return True

    if re.fullmatch(r'[\d\s\.,\-/]+', low):
        return True

    profile = detect_document_profile(doc_title)
    for pat in profile.get("noise_patterns", ()):
        if re.search(pat, low, re.IGNORECASE):
            return True
    return False


def evaluate_parsing_quality(doc_title: str, rows: list[str]) -> dict:
    """Оценивает чистоту и полноту распознавания строк для выбранного профиля РД."""
    profile = detect_document_profile(doc_title)
    clean_cnt = 0
    dropped_cnt = 0
    for r in rows:
        if is_noise_for_document(doc_title, r):
            dropped_cnt += 1
        else:
            clean_cnt += 1
    total = len(rows)
    score_pct = round((clean_cnt / total) * 100, 1) if total else 100.0
    return {
        "profile_code": profile["code"],
        "profile_name": profile["name"],
        "section": profile["section"],
        "total": total,
        "clean": clean_cnt,
        "dropped": dropped_cnt,
        "quality_pct": score_pct,
    }
def resolve_section_and_brigade(section_code):
    code = str(section_code or "РД").upper().strip()
    rules = {
        "АР": ("Архитектурные решения (АР)", "СП 71.13330.2017", "https://cntd.ru", "Звено отделочников и каменщиков", "Кладка, перегородки, отделка и полы"),
        "КЖ": ("Конструкции железобетонные (КЖ)", "СП 63.13330.2018", "https://cntd.ru", "Бригада монолитчиков", "Опалубка, армирование и бетонирование"),
        "ЭС": ("Электроснабжение и освещение (ЭС)", "ПУЭ (7-е изд.)", "https://cntd.ru", "Звено электромонтажников", "Кабельные трассы, щиты ВРУ/ГРЩ и контур заземления"),
        "СПА": ("Пожарная автоматика (СПА / АПС)", "СП 484.1311500.2020", "https://cntd.ru", "Звено слаботочников и ПНР", "Приборы ППКУ, извещатели, ОКЛ и огнезащита"),
        "ОВ": ("Отопление и вентиляция (ОВиК)", "СП 60.13330.2020", "https://cntd.ru", "Звено монтажников ОВиК", "Воздуховоды, узлы обвязки и теплоизоляция"),
        "ВК": ("Водоснабжение и канализация (ВК)", "СП 30.13330.2020", "https://cntd.ru", "Звено сантехников-монтажников", "Трубопроводы ПНД/ППР, выпуск К1 и испытания"),
        "ГП": ("Генплан и наружные сети (ГП)", "СП 42.13330.2016", "https://cntd.ru", "Звено дорожных рабочих", "Вертикальная планировка, колодцы и благоустройство"),
    }
    for prefix, data in rules.items():
        if prefix in code:
            return {"section": data, "snip_ref": data[1], "snip_url": data[2], "brigade": data[3], "duty": data[4]}
    return {
        "section": f"Рабочая документация ({code})",
        "snip_ref": "ГОСТ 21.1101-2013",
        "snip_url": "https://cntd.ru",
        "brigade": "Универсальное звено ПТО",
        "duty": "Монтаж и контроль по рабочей документации",
    }
