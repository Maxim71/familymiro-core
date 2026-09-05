# ==============================================================================
#          БЛОК 63: ТЕСТОВЫЙ СКРИПТ ОТПРАВКИ ИИ-ТЕХНАДЗОРА (test_gate.py)
# ==============================================================================

import os
import zipfile
import requests

# Настройки подключения к нашему боевому серверу
SERVER_IP = "91.229.10.66"
URL = f"http://{SERVER_IP}/api/v1/monolith/gateway/"  # Путь к Высшему Шлюзу

ZIP_FILENAME = "floor_photos_axes_C_G.zip"
TEST_IMAGE = "photo_room_107.jpg"

def create_mock_assets():
    """ Создает фейковое фото и упаковывает в ZIP, имитируя отчет прораба """
    print("[1.5] Шаг 1: Формируем файлы фотофиксации зоны полов по осям C-G...")
    
    # Создаем пустой файл под видом фотографии опрессовки REHAU
    with open(TEST_IMAGE, "w") as f:
        f.write("MOCK_IMAGE_DATA_REHAU_COLLECTOR_ROOM_107")
        
    # Запаковываем в ZIP-архив, как требует наш всеядный парсер Блока 70
    with zipfile.ZipFile(ZIP_FILENAME, 'w') as zipf:
        zipf.write(TEST_IMAGE)
        
    # Зачищаем одиночный файл, оставляем только архив
    if os.path.exists(TEST_IMAGE):
        os.remove(TEST_IMAGE)
    print(f"[1.5] Архив '{ZIP_FILENAME}' успешно собран и готов к прыжку.")


def send_to_monolith():
    """ Отправляет архив и метаданные через Трёхконтурный Шлюз """
    if not os.path.exists(ZIP_FILENAME):
        create_mock_assets()
        
    print(f"[1.5] Шаг 2: Пробиваем финансово-технический шлюз на {SERVER_IP}...")
    
    # Данные транзакции и спецификации объекта для расчета лимитов Овика и налога LAVA API
    payload = {
        "project_id": "1",               # ID нашего объекта в базе PostgreSQL
        "amount": "150000.00",           # Сумма акта RFI за наливные полы в рублях
        "is_agro": "False"               # Отключаем вектор AGRO_RESONANCE, это стройка
    }
    
    try:
        with open(ZIP_FILENAME, 'rb') as f:
            files = {'file': (ZIP_FILENAME, f, 'application/zip')}
            
            # Отправка POST-запроса прямо в ядро Монолита
            response = requests.post(URL, data=payload, files=files, timeout=10)
            
        print("\n" + "="*70)
        print(f"[1.5] ОТВЕТ ОТ СЕРВЕРА (Статус {response.status_code}):")
        print("="*70)
        
        if response.status_code == 200:
            data = response.json()
            print(f"🧬 Статус Блока 63 : {data.get('block_63_status')}")
            print(f"📐 Сфера ИИ-Детекции : {data.get('detected_sphere')}")
            print(f"📝 Инструкция Мастеру: {data.get('floor_instruction')}")
            print("\n📊 РАСЩЕПЛЕНИЕ ПРИБЫЛИ LAVA API:")
            split = data.get('financial_split', {})
            print(f"  🔹 Налог в ФНС РФ (6%): {split.get('fns_tax_paid_rub')} руб.")
            print(f"  💎 Запечатано в Сейф Наследницы: {split.get('vault_deposited_usd')} USD")
            print(f"  👑 Моментальная Отцовская Премия: {split.get('father_instant_cash')} USD")
            print(f"\n🦔 Рапорт: {data.get('msg')}")
        else:
            print(f"❌ Ошибка шлюза: {response.text}")
            
    except Exception as e:
        print(f"❌ Не удалось связаться с сервером: {str(e)}")
    finally:
        # Убираем за собой тестовый архив
        if os.path.exists(ZIP_FILENAME):
            os.remove(ZIP_FILENAME)

if __name__ == "__main__":
    send_to_monolith()
