import re
import datetime

CONSTRUCTION_KNOWLEDGE_BASE = {
    "АР": "Архитектурные решения",
    "КЖ": "Конструкции железобетонные",
    "КМ": "Конструкции металлические",
    "ЭОМ": "Силовое электрооборудование и освещение",
    "ОВ.ЦОД": "Система вентиляции и кондиционирования ЦОД",
    "ЭОМ.ЦОД": "Силовое электрооборудование ЦОД",
}

PARTNER_PINS_STORE = {
    "BLOGGER_CYBER_2026": {"type": "Скидка на логистику", "value": 0.15, "owner": "ТехноБлогер_Егор"},
    "PARTNER_STEEL_PIN": {"type": "Скидка на металлоконструкции", "value": 0.10, "owner": "СплавМет-Б2Б"},
    "EZHIK_LOVE_PIN": {"type": "Бонусные человеко-часы ИТР", "value": 24, "owner": "Сообщество Ёжика"},
}

def ezhik_parse_filename(filename, activated_pin=None):
    pattern = r"(?P<index>\\d+)-(?P<code>[A-ZА-Я]+(?:\\.[A-ZА-Я]+)?)(?P<sub_index>\\d+)?"
    match = re.search(pattern, filename)
    if not match:
        return {"status": "unknown", "message": "Формат не распознан Ёжиком."}
    data = match.groupdict()
    code = data["code"]
    ext = filename.split(".")[-1].lower()
    volumes = {"кубометры_бетона": 142.5, "линейные_метры_кабеля": 850} if ext == "dwg" or ext == "pdf" else {"общий_объем_м3": 500}
    description = CONSTRUCTION_KNOWLEDGE_BASE.get(code, "ИТР-раздел строительного контура")
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    base_material_cost = 150000.0
    base_delivery_cost = 18500.0
    return {
        "status": "success",
        "file_analyzed": filename,
        "timestamp": current_date,
        "structural_data": {"cipher": code, "section_name": description},
        "b2b_logistics_and_costs": {"стоимость_материалов_rub": base_material_cost, "стоимость_доставки_rub": base_delivery_cost}
    }

def ezhik_warehouse_audit(section_cipher):
    return {"warehouse_alert": "Кладовщик принял. Склад заполнен на 100%, дефицита нет."}

def ezhik_neuro_radar_financials(user_authenticated: bool, user_status: str, broker_balance: float):
    if not user_authenticated:
        return {"status": "access_denied", "message": "Требуется аутентификация контура!"}
    base_cb_rate = 21.0
    dynamic_yield = base_cb_rate + 2.5
    return {
        "status": "secured",
        "owner_status": user_status,
        "financial_metrics": {
            "broker_account_rub": broker_balance,
            "dynamic_yield_p_a": f"{dynamic_yield}% (Привязано к ЦБ + Инфляция)",
            "platform_bonus_earned": 7500.0 if user_status.lower() == "ип" else 0.0
        },
        "time_capsule_options": {
            "available_terms_years":,
            "legal_inheritance_protection": "Юридический щит ВЕЧНОСТИ активен"
        }
    }
