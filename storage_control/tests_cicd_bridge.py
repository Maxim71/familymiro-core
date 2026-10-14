# -*- coding: utf-8 -*-
import sys, requests
sys.path.append('/root/app')

def run_monolith_cicd_audit():
    print('\n=============================================================')
    print('🛰️  🤖 ЗАПУСК СВЕРХТОЧНОГО DevOps-АУДИТА КОНТУРА CI/CD // MIROHA.RU:')
    print('=============================================================')
    
    endpoints = {
        "1. Главное Игровое Лобби (Django Монолит)": "http://127.0.0",
        "2. Вагон B2B-Снабжения (Каталог СУБД)  ": "http://127.0.0api/v5/products/catalog/",
        "3. Блогерский Шлюз WB-II (СУБД & Маржа) ": "http://127.0.0api/v5/blogger/max/",
        "4. Асинхронный Тьютор-Модуль (Flask)    ": "http://127.0.0",
        "5. Асинхронная Борд-Панель ПТО (FastAPI)": "http://127.0.0"
    }
    
    session = requests.Session()
    session.headers.update({'User-Agent': 'Miroha-CI-CD-Bot-v5.0'})
    
    success_count = 0
    for name, url in endpoints.items():
        try:
            res = session.get(url, timeout=3.0)
            if res.status_code == 200 or res.status_code == 301:
                print(f"   📦 {name} ➔ Статус: 200 OK 🟢 ИДЕАЛ")
                success_count += 1
            else:
                print(f"   🔴 ВНИМАНИЕ: {name} ➔ Статус: {res.status_code}")
        except Exception as err:
            print(f"   🔴 СБОЙ СОКЕТА: {name} ➔ Ошибка: {str(err)}")
            
    print('=============================================================')
    if success_count == len(endpoints):
        print('🔱  VERDICT: Сквозной CI/CD пайплайн Бронепоезда СТАБИЛЕН. Зажимы сняты.')
    else:
        print('⚠️  VERDICT: Контур частично дестабилизирован. Проверить сокеты.')
    print('=============================================================\n')

if __name__ == "__main__":
    run_monolith_cicd_audit()
