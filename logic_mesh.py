import pandas as pd
import json
import os

def check_and_create_json():
    """Направление 1: ИИ-Автовосстановление файла базы данных при его отсутствии"""
    filename = "blueprint_mesh.json"
    if not os.path.exists(filename):
        default_data = {
          "contours": [
            {"id": 1, "name": "Contour_1_Mars_Axis_3-6", "material": "Бетон Б25", "volume_m2": 480.2, "snip_hours": 160, "fact_hours": 142, "cost_rub": "4,850,000.00", "status_1c": "СИНХРОННО"},
            {"id": 2, "name": "Contour_2_Neptune_Axis_1-2", "material": "Сухие смеси Limonapro / Отделка С-2", "volume_m2": 1240.5, "snip_hours": 240, "fact_hours": 195, "cost_rub": "2,120,000.00", "status_1c": "ДОСТАВКА ХАБ"}
          ]
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=2, ensure_ascii=False)

def get_b2b_stock_table():
    """Срез ведомости сравнения проектных лимитов АР из PDF и живого склада 1С"""
    check_and_create_json()
    supply_data = {
        "📦 ИТР-Категория": [
            "1. Отделочные материалы (Финиш С-2)", 
            "2. Строительный Инструмент (Уровни)", 
            "3. Расходные части (Стеклохолст)"
        ],
        "📐 Спецификация АР из PDF": ["1,240.50 м²", "12 компл.", "1,500.00 пог.м"],
        "🏬 Живой Склад 1С": ["1,400.00 м² (Запас)", "8 компл. (Дефицит!)", "300.00 пог.м (Нуль!)"],
        "🔄 ИИ-Статус Цепочки Одобрения": [
            "🟢 В КАНАЛЕ (Равновесие)", 
            "🟡 ОЖИДАЕТ ОДОБРЕНИЯ", 
            "🔴 СОРВАН ЛИМИТ (Кокосовод)"
        ]
    }
    return pd.DataFrame(supply_data)

def generate_m15_xml_package(axis_name):
    """Генератор XML-кода требования-накладной М-15 для таблицы b2b_supply_orders_oks"""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<NasaSyndicateExport version="24.0">
    <Meta author="Архитектор_Создатель" database="b2b_supply_orders_oks"/>
    <ITR_Tabel_Data axis="{axis_name.upper()}" floor="5" block="Б-4">
        <Material name="Латексная краска Lakra" required_kg="100" issued_buckets="20"/>
        <Labor snip_hours="240" status="VERIFIED_BY_ASR"/>
    </ITR_Tabel_Data>
</NasaSyndicateExport>"""
