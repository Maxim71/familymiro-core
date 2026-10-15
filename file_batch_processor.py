# -*- coding: utf-8 -*-
import os
import re
import pandas as pd
from pypdf import PdfReader
from storage_control.logic_core import EzhikIntentClassifier

def auto_tag_document(file_path):
    """🦔 РОБОТ-ЁЖИК: Читает смету и вырезает векторные интенты, ГОСТы и объемы"""
    ext = os.path.splitext(file_path)[-1].lower()
    extracted_text = ""
    
    try:
        if ext == ".pdf":
            reader = PdfReader(file_path)
            for page in reader.pages:
                extracted_text += page.extract_text() or ""
        elif ext in [".xlsx", ".xls"]:
            df = pd.read_excel(file_path)
            extracted_text = " ".join(df.astype(str).values.flatten())
        elif ext == ".csv":
            df = pd.read_csv(file_path)
            extracted_text = " ".join(df.astype(str).values.flatten())
    except Exception as e:
        return {"intent": "PARSING_ERROR", "material_subcaste": "NONE", "gosts": [], "volumes": [], "error": str(e)}

    classifier = EzhikIntentClassifier()
    return classifier.classify(extracted_text)

def run_batch_markup_to_excel(target_dir, output_excel_path):
    """🎰 ПАКЕТНЫЙ ЭКСПОРТ: Сканирует папку со сметами и лепит ИТР-таблицу Excel"""
    print(f"[Парсер] Запуск сканирования директории: {target_dir}")
    
    reports = []
    if not os.path.exists(target_dir):
        os.makedirs(target_dir, exist_ok=True)
        # Создаем тестовую заглушку для проверки, если папка пуста
        with open(os.path.join(target_dir, "test_smeta.txt"), "w", encoding="utf-8") as f:
            f.write("Доставка миксером БСТ М400 в объеме 35 м3 по ГОСТ 7473-2010 склад-::-спецификация")

    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith(('.pdf', '.xlsx', '.xls', '.csv', '.txt')):
                full_path = os.path.join(root, file)
                print(f"[Сканер] Обработка файла: {file}")
                
                # Если файл текстовый, читаем напрямую, иначе через парсеры документов
                if file.endswith('.txt'):
                    with open(full_path, 'r', encoding='utf-8') as f: txt = f.read()
                    classifier = EzhikIntentClassifier()
                    res = classifier.classify(txt)
                else:
                    res = auto_tag_document(full_path)
                
                reports.append({
                    "Имя Файла": file,
                    "Основной Интент Яндекса": res.get("intent", "SAMOZAN"),
                    "Подкластер Материала": res.get("material_subcaste", "NONE"),
                    "Вытащенные ГОСТы": ", ".join(res.get("extracted_gosts", [])),
                    "Физический Объем": ", ".join([f"{v[0]} {v[1]}" for v in res.get("extracted_volumes", [])]),
                    "Маркер Сцепки Склада": "АКТИВЕН" if res.get("has_separator") else "НЕТ"
                })

    # Силой pandas лепим красивую ИТР-таблицу Excel
    df_report = pd.DataFrame(reports)
    df_report.to_excel(output_excel_path, index=False)
    print(f"[УСПЕХ] Вся база автоматически размечена! Отчет сохранен: {output_excel_path}")

if __name__ == "__main__":
    run_batch_markup_to_excel("/root/app/storage/", "/root/app/ii_markup_report.xlsx")
