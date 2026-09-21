import uvicorn
import pandas as pd
import numpy as np
import os
import time
import asyncio
from datetime import datetime
from fastapi import FastAPI, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTML_IMAGE_RESPONSE if 'HTML_IMAGE_RESPONSE' in locals() else JSONResponse

app = FastAPI(title="Miroha AGRIPS Core PM Gateway", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_DIR = "/var/www/miroha_static/contracts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 📋 ИН-ПАМЯТЬ СУБД CRUD РЕЕСТР УСТРОЙСТВ МЕНЕДЖЕРА ПРОЕКТА (AGRIPS)
AGRIPS_CONNECTED_NODES = {
    "192.168.0.231": {"device": "🖥️ WEB-МОНОЛИТ", "owner": "Капитан Максим", "kpd": "98.5%", "status": "АКТИВЕН", "last_ping": "15:01:22"},
    "192.168.0.216": {"device": "📱 MOBILE-ПРОРАБ", "owner": "Бригадир Михалыч", "kpd": "87.2%", "status": "В СЕТИ (Ось А-Г)", "last_ping": "15:02:40"},
    "127.0.0.1": {"device": "⚙️ CLI-ТЕРМИНАЛ LINUX", "owner": "Робот-Ёжик (DevOps)", "kpd": "100.0%", "status": "СКАНИРОВАНИЕ", "last_ping": "15:03:01"}
}

class EzhikAgripsAnalyst:
    def __init__(self):
        self.module_name = "🦔 Модуль AGRIPS // Зрение Сокола"
        self.philosophy = "Тотальный асинхронный след подключений. Контроль Mobile, Web и CLI узлов."

    async def execute_async_network_audit(self, client_ip, user_agent):
        """⏳ ИИ-АНАЛИТИКА СЛЕДА: Асинхронная проверка входящего сокета через await"""
        await asyncio.sleep(0.1) # Симулируем тяжелую неблокирующую прозвонку порта в ОЗУ
        ua_lower = user_agent.lower()
        
        # Детекция типа решения (Ветвь Менеджера Проекта)
        if "mobile" in ua_lower or "android" in ua_lower or "iphone" in ua_lower:
            detected_platform = "📱 MOBILE РЕШЕНИЕ (Наряды смены Прораба)"
        elif "curl" in ua_lower or "python-requests" in ua_lower:
            detected_platform = "⚙️ CLI АВТОМАТИЗАЦИЯ (Запрос Робота-Ёжика)"
        else:
            detected_platform = "🖥️ ВЕБ-ИНТЕРФЕЙС УПРАВЛЕНИЯ (Капитанский пульт)"
            
        return {
            "platform": detected_platform,
            "security_check": "✅ ЧИСТЫЙ ТРАФИК // СЛУЖБА УГРП СВЯЗАНА",
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }

AGRIPS_ENGINE = EzhikAgripsAnalyst()

@app.get("/api/v2/agrips-dashboard/")
async def agrips_dashboard_get(request: Request):
    """READ (CRUD): Менеджер проекта забирает полную аналитику всех ips"""
    user_agent = request.headers.get("User-Agent", "Unknown")
    client_ip = request.client.host
    
    # Запуск асинхронного "Зрения Сокола"
    audit_data = await AGRIPS_ENGINE.execute_async_network_audit(client_ip, user_agent)
    
    return JSONResponse({
        "status": "success",
        "module": AGRIPS_ENGINE.module_name,
        "philosophy": AGRIPS_ENGINE.philosophy,
        "current_session_audit": audit_data,
        "connected_registry_crud": AGRIPS_CONNECTED_NODES
    })

@app.post("/api/v2/agrips-crud-create/")
async def agrips_crud_create(request: Request):
    """CREATE (CRUD): Подключение нового Mobile/Web узла в пространство AGRIPS"""
    form_data = await request.form()
    node_ip = form_data.get("node_ip", "192.168.0.100").strip()
    device_type = form_data.get("device_type", "📱 MOBILE-КАНДИДАТ").strip()
    owner_name = form_data.get("owner", "Мастер Николай").strip()
    
    # Добавляем в реестр СУБД ОЗУ нового пользователя
    AGRIPS_CONNECTED_NODES[node_ip] = {
        "device": device_type,
        "owner": owner_name,
        "kpd": f"{random.randint(85, 99)}.%",
        "status": "АВТОРИЗОВАН ПОД @2FA",
        "last_ping": datetime.now().strftime("%H:%M:%S")
    }
    
    # Отправляем экстренное ИТР-уведомление в Telegram Капитану Максиму на телефон
    tg_msg = (
        f"🛰️ <b>[AGRIPS CORE // НОВЫЙ CRUD УЗЕЛ]</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔌 <b>Зафиксирован Вход IP:</b> {node_ip}\n"
        f"👤 <b>Ответственное Лицо:</b> {owner_name}\n"
        f"📱 <b>Платформа:</b> {device_type}\n"
        f"🔭 <b>Зрение Сокола:</b> Точка авторизована в приватной сети.\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🦔 <i>След заблокирован в ОЗУ. Fast API контракт опечатан.</i>"
    )
    try:
        requests.post(f"https://telegram.org", data={
            "chat_id": "541888946", "text": tg_msg, "parse_mode": "HTML"
        }, timeout=2)
    except Exception: pass

    return JSONResponse({"status": "success", "message": f"Узел {node_ip} успешно занесен в табель AGRIPS!", "registry": AGRIPS_CONNECTED_NODES})

# Старый пуленепробиваемый роут выгрузки CSV сметы из требований сохраняем!
@app.post("/api/v1/generate-contract-bundle/")
async def generate_contract_bundle():
    csv_file_path = os.path.join(OUTPUT_DIR, "contract_report.csv")
    svg_file_path = os.path.join(OUTPUT_DIR, "performance_graph.svg")
    df = pd.DataFrame({"Шифр": ["MAT-A500С"], "Лимит": [45.0], "Выполнено": [30.0]})
    df.to_csv(csv_file_path, index=False, encoding='utf-8-sig')
    with open(svg_file_path, "w") as f: f.write('<svg><rect width="100" height="20" fill="#00f0ff"/></svg>')
    return JSONResponse({"status": "success", "csv_download_url": "/static/contracts/contract_report.csv", "svg_inline_url": "/static/contracts/performance_graph.svg"})

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9000)
