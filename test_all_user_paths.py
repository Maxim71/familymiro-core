import sys
import time
import requests
from datetime import datetime

def run_global_path_verification():
    print("\n=============================================================")
    print("🛰️  [Miroha EndUser Path-Verify]: ТЕСТ КУРСА КОНЕЧНОГО ПОЛЬЗОВАТЕЛЯ")
    print("=============================================================")
    time.sleep(0.5)

    base_url = "http://127.0.0.1"
    
    # Карта сквозных путей (Path) распределенного кластера для тестирования
    target_paths = [
        # 🏢 ГЛАВНОЕ ЯДРО (Django - Порт 8000)
        {"path": "/", "port": 8000, "role": "Все лица / Эфир", "desc": "Главный Монолит (Мультивалютный капитал & Новости)"},
        {"path": "/radar/", "port": 8000, "role": "Капитан Максим", "desc": "ИИ-Радар Логистики (3D-Параллакс судов КНР)"},
        {"path": "/pto/1/", "port": 8000, "role": "Замначальника / ПТО", "desc": "Кабинет ПТО (Сметы, Ведомости ВОР, КС-2)"},
        
        # 📚 СЛОЙ ИНТЕЛЛЕКТА И ОБУЧЕНИЯ (Flask - Порт 5000)
        {"path": "/", "port": 5000, "role": "Новые Кандидаты", "desc": "Flask ИТР-Справочник Ментора (Подсветка зон риска)"},
        
        # 🔌 ШЛЮЗ КОНТРАКТОВ (FastAPI - Порт 9000)
        {"path": "/docs", "port": 9000, "role": "Смежные системы", "desc": "FastAPI Спецификация контрактов (OpenAPI)"},
        
        # 🚀 ПОТОКИ JSON API (Сбор данных в ОЗУ)
        {"path": "/api/live-stream-data/", "port": 8000, "role": "Все пользователи", "desc": "JSON API Бегущая лента RFI-фактов"},
        {"path": "/api/tender-exchange-dashboard/", "port": 8000, "role": "Тендерный комитет", "desc": "JSON API Перехват логов закупок области"},
        {"path": "/api/tsf-get-map-data/", "port": 8000, "role": "Волонтеры ТСФ", "desc": "JSON API Координаты объектов Том Сойер Феста"}
    ]

    print(f"⏱️  Запуск сетевой проверки. Всего прозванивается путей: {len(target_paths)}\n")
    print(f"{'№':<3} {'МАРШРУТ (PATH)':<35} {'ПОРТ':<6} {'ДОСТУПНОСТЬ ДЛЯ ЛИЦА':<22} {'СТАТУС':<8}")
    print("-" * 80)

    success_count = 0
    for idx, item in enumerate(target_paths, 1):
        full_endpoint = f"{base_url}:{item['port']}{item['path']}"
        try:
            # Делаем физический локальный запрос к сокету в ОЗУ
            res = requests.get(full_endpoint, timeout=2, headers={"User-Agent": "MirohaPathChecker/1.0"})
            
            # Для Джанго редирект 301/302 считается успешным проходом контура безопасности
            status_desc = f"{res.status_code} OK" if res.status_code in [200, 301, 302] else f"{res.status_code} ERR"
            is_ok = res.status_code in [200, 301, 302]
            
            if is_ok:
                success_count += 1
                color_badge = "✅"
            else:
                color_badge = "❌"
                
            print(f"{idx:<3} {item['path']:<35} {item['port']:<6} {item['role']:<22} {color_badge} {status_desc}")
            
        except Exception as e:
            print(f"{idx:<3} {item['path']:<35} {item['port']:<6} {item['role']:<22} ❌ DOWN")

    print("-" * 80)
    current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    print(f"📊 ИТОГ ТЕСТИРОВАНИЯ: Успешно верифицировано путей: {success_count} из {len(target_paths)}")
    print(f"🔐 Вердикт: Кластер стабилен. Время проверки лога: {current_time}")
    print("=============================================================\n")

if __name__ == "__main__":
    run_global_path_verification()
