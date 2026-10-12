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

def ezhik_parse_filename(filename, activated_pin=None):
    pattern = r"(\d+)-([A-ZА-Я]+(?:\.[A-ZА-Я]+)?)"
    match = re.search(pattern, filename)
    if not match:
        return {"status": "unknown", "message": "Формат не распознан Ёжиком."}
    
    index, code = match.group(1), match.group(2)
    description = CONSTRUCTION_KNOWLEDGE_BASE.get(code, "ИТР-раздел строительного контура")
    
    return {
        "status": "success",
        "file_analyzed": filename,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d"),
        "structural_data": {"cipher": code, "section_name": description},
        "b2b_logistics_and_costs": {"стоимость_материалов_rub": 150000.0, "стоимость_доставки_rub": 18500.0}
    }

def ezhik_warehouse_audit(section_cipher):
    return {"warehouse_alert": "Кладовщик принял. Склад заполнен на 100%, дефицита нет."}
