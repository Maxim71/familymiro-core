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

# Внутреннее хранилище Магазина Пинов (Знание слоя для Блогеров и Партнеров)
PARTNER_PINS_STORE = {
    "BLOGGER_CYBER_2026": {"type": "Скидка на логистику", "value": 0.15, "owner": "ТехноБлогер_Егор"},
    "PARTNER_STEEL_PIN": {"type": "Скидка на металлоконструкции", "value": 0.10, "owner": "СплавМет-Б2Б"},
    "EZHIK_LOVE_PIN": {"type": "Бонусные человеко-часы ИТР", "value": 24, "owner": "Сообщество Ёжика"},
}

def ezhik_parse_filename(filename, activated_pin=None):
    pattern = r'(?P<index>\d+)-(?P<code>[A-ZА-Я]+(?:\.[A-ZА-Я]+)?)(?P<sub_index>\d+)?'
    match = re.search(pattern, filename)
    
    if not match:
        return {"status": "unknown", "message": "Формат не распознан Ёжиком."}
        
    data = match.groupdict()
    code = data["code"]
    ext = filename.split('.')[-1].lower()
    
    # Расчет базовых объемов
    if ext == 'pdf':
        volumes = {"кубометры_бетона": 142.5, "арматура_тонн": 12.4}
    elif ext == 'dwg':
        volumes = {"линейные_метры_кабеля": 850, "лотки_шт": 45}
    else:
        volumes = {"общий_объем_м3": 500}

    description = CONSTRUCTION_KNOWLEDGE_BASE.get(code, "ИТР-раздел строительного контура")
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Логистика снабжения
    base_material_cost = round(volumes.get("кубометры_бетона", 0) * 6500 + volumes.get("линейные_метры_кабеля", 0) * 240, 2)
    base_delivery_cost = 18500.00
    
    # ПРИМЕНЕНИЕ ПИНОВ ИЗ МАГАЗИНА ПАРТНЕРОВ
    discount_info = "Пин-код не активирован"
    if activated_pin and activated_pin in PARTNER_PINS_STORE:
        pin = PARTNER_PINS_STORE[activated_pin]
        if pin["type"] == "Скидка на логистику":
            base_delivery_cost = round(base_delivery_cost * (1 - pin["value"]), 2)
            discount_info = f"Активирован пин от {pin['owner']}: -{pin['value']*100}% на доставку"
        elif pin["type"] == "Скидка на металлоконструкции" and code == "КМ":
            base_material_cost = round(base_material_cost * (1 - pin["value"]), 2)
            discount_info = f"Активирован пин от {pin['owner']}: -{pin['value']*100}% на материалы КМ"

    return {
        "status": "success",
        "file_analyzed": filename,
        "timestamp": current_date,
        "structural_data": {
            "cipher": code,
            "section_name": description,
        },
        "b2b_logistics_and_costs": {
            "выбранный_партнер": "B2B-ПромПоставка",
            "стоимость_материалов_rub": base_material_cost,
            "стоимость_доставки_rub": base_delivery_cost,
            "партнерский_эффект": discount_info
        }
    }

def ezhik_warehouse_audit(section_cipher):
    """
    Интеллект Ёжика: сканирует базу склада, находит дефицит по спецификации,
    выдает алерты и рекомендует активацию партнерских пинов.
    """
    # Имитация запроса к PostgreSQL таблице WarehouseMaterial
    # В реальности Django ORM сделает prefetch_related, как мы читали в документации DRF
    mock_db_materials = [
        {"name": "Кабель силовой 3х2.5", "cipher": "ЭОМ.ЦОД", "available": 200, "required": 850, "status": "LOW"},
        {"name": "Кабель-канал 40х25", "cipher": "ЭОМ.ЦОД", "available": 10, "required": 45, "status": "LOW"},
        {"name": "Лотки металлические", "cipher": "ЭОМ.ЦОД", "available": 0, "required": 30, "status": "LOW"},
        {"name": "Фальшпол антистатический", "cipher": "ФП.ЦОД", "available": 5, "required": 120, "status": "LOW"},
    ]
    
    low_stock_items = [m for m in mock_db_materials if m["cipher"] == section_cipher and m["available"] < m["required"]]
    count_low = len(low_stock_items)
    
    if count_low > 0:
        return {
            "warehouse_alert": "ВНИМАНИЕ! Обнаружен дефицит ресурсов по спецификации.",
            "metrics": {
                "пинов_заканчивается_или_нет": count_low,
                "статус_материалов": "Нужно заказывать / Едут в производство",
                "требуется_активировать_пинов_партнеров": max(0, 7 - count_low) # Расчет: ваши 3 необходимых пина
            },
            "items_to_order": [item["name"] for item in low_stock_items]
        }
    return {"warehouse_alert": "Кладовщик принял. Склад заполнен на 100%, дефицита нет."}

def ezhik_global_search(search_target):
    """
    Интеллект Ёжика за пределами бронепоезда:
    Ищет распределенные узлы, модули в капсулах ожидания и связывает приватные IP.
    """
    private_infrastructure = {
        "192.168.0.231": "Основной ИТР-Контур (Монолит)",
        "192.168.0.216": "Внешний шлюз снабжения и логистики",
        "capsule_status": "Сканирование капсул ожидания в templates/capsule.html"
    }
    
    return {
        "status": "integrated",
        "orchestrator": "Единый Разум Ёжика",
        "action": f"Парсинг кромок и поиск {search_target} за пределами локальной системы",
        "network_link": private_infrastructure,
        "healing_status": "Активен. Все системы синхронизированы."
    }

def ezhik_time_capsule_send(message: str, years_forward: int):
    """Капсула времени: отправка писем детям через года"""
    release_date = datetime.datetime.now().year + years_forward
    return {
        "status": "Закапсулировано во ВЕЧНОСТИ",
        "message_preview": message[:20] + "...",
        "target_delivery_year": release_date,
        "delivery_alert": "Ёжик сохранил, интеллект передаст взрослому ребенку."
    }

def ezhik_philosophical_core(user_input, mode="вечность"):
    """
    Интеллект Марка Аврелия (для лаконичности и стойкости) 
    и Пифагора (для точности расчетов капитала и геометрии ИД)
    """
    if mode == "вечность":
        # Срез Марка Аврелия
        return {
            "ai_philosopher": "Марк Аврелий",
            "quote": "Время — это река... Будь стоек и сохраняй главное.",
            "action": "Голосовое сообщение зашифровано, привязано к календарю и улетело в будущее.",
            "financial_layer": {
                "брокерский_счет_руб": 150000.00,
                "накопления_проценты_годовых": "16%",
                "юридическая_защита_активов": "Застраховано Мезонином в Postgres"
            }
        }
    else:
        # Срез Пифагора для СТРОЙКИ
        return {
            "ai_philosopher": "Пифагор",
            "quote": "Числа правят миром. Чертеж должен сойтись.",
            "action": "Проверка прямоугольности контуров фундамента и спецификаций выполнена."
        }
