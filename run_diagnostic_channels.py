# -*- coding: utf-8 -*-
import socket
import sys
import subprocess

print("=====================================================================")
print("🪲 РАСШИРЕННЫЙ ИТР-ТЕСТ КАНАЛОВ И СЛУЖБ БРОНЕПОЕЗДА // СИНДИКАТ МАКСИМА")
print("=====================================================================")

def check_port(port, name):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1.5)
    try:
        s.connect(('127.0.0.1', port))
        print(f"[СЛУЖБА ОК] --> {name} на порту {port} УСПЕШНО НАЙДЕН В ОЗУ ХОСТА!")
        s.close()
        return True
    except:
        print(f"[КРИТИЧЕСКИЙ ЗАСОР] --> {name} на порту {port} МЕРТВ ИЛИ ЗАБЛОКИРОВАН!")
        return False

# 1. Простукиваем сокеты хостинга
ports_to_check = {
    5432: "СУБД Постгрес (miro_postgres_evolution)",
    6379: "Кэш-Брокер Редис (miro_redis_broker)",
    8000: "Веб-Монолит Джанго (miro_web_monolith)",
    5000: "Маркетинг Flask (app_flask.py)",
    8888: "Асинхронный Торнадо (app_tornado.py)"
}

print("\n[Шаг 1/3] Проверка физической активности портов в памяти:")
all_ok = True
for port, name in ports_to_check.items():
    if not check_port(port, name):
        all_ok = False

# 2. Проверяем системные цепочки Docker в ядре iptables
print("\n[Шаг 2/3] Проверка целостности цепочек Docker в iptables хоста:")
try:
    res = subprocess.run(["sudo", "iptables", "-t", "nat", "-L", "DOCKER"], capture_output=True, text=True)
    if res.returncode == 0:
        print("[СЕТЬ ОК] Системная цепочка DOCKER в ядре Linux жива и стабильна!")
    else:
        print("[КРИТИЧЕСКИЙ ЗАСОР] Цепочка DOCKER разрушена! Требуется systemctl restart docker!")
except Exception as e:
    print(f"[КРИТИЧЕСКИЙ ЗАСОР] Ошибка проверки брандмауэра: {e}")

# 3. Сканируем логи застрявшего веб-Монолита
print("\n[Шаг 3/3] Вытаскиваем скрытые вылеты контейнера Джанго из логов Докера:")
os.system("sudo docker logs miro_web_monolith 2>&1 | tail -n 10")
print("=====================================================================")
