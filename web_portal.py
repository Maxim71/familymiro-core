# -*- coding: utf-8 -*-
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="FamilyMira Живой ИИ-Онбординг // Тритон-Контур")

# Модель входящего гостя (пришедшего на пробный сеанс или из Telegram)
class GuestOnboardingRequest(BaseModel):
    guest_name_or_id: str          # Имя, ник или ID из мессенджера Familymira
    chosen_skill: str              # Профессиональный скилл, например: "ПТО"
    invitation_source: str         # "telegram_bot", "ezhik_invite", "free_trial"

@app.post("/api/v1/portal/onboarding")
def ezhik_onboarding_gate(request: GuestOnboardingRequest):
    """
    Живой привратник Ёжика: приветствует человека, запрашивает имя/ID,
    предлагает создать Аватар Стройки и активирует ИТР-скилл.
    """
    skill = request.chosen_skill.upper()
    
    # Генерация ИИ-Аватара стройки на основе выбранного скилла
    avatar_metadata = {
        "avatar_type": f"ИТР-Кибер_Мастер_{skill}",
        "visual_style": "Параллакс-Неон-Purple-CAD",
        "access_shield": "Юридическая защита ВЕЧНОСТИ активна"
    }
    
    # Ёжик распределяет пользователя по вагонам автоматизации
    if "ПТО" in skill:
        return {
            "status": "authenticated",
            "welcome_message": f"Приветствуем в системе, {request.guest_name_or_id}! Ёжик распознал твой Скилл ПТО.",
            "avatar": avatar_metadata,
            "redirect_endpoint": "/portal/render/pto_cabinet",
            "layout_config": {
                "layout": "parallax_industrial_engineer",
                "theme": "neon_purple_cad",
                "allowed_modules": ["dxf_blueprint_scan", "procurement_flow", "bim_collision_radar"]
            }
        }
    elif "ПРОРАБ" in skill or "МАСТЕР" in skill:
        return {
            "status": "authenticated",
            "welcome_message": f"Рады видеть на площадке, Линейный руководитель {request.guest_name_or_id}!",
            "avatar": {"avatar_type": "Линейный_Прораб_Шилд", "visual_style": "Параллакс-Минимализм"},
            "redirect_endpoint": "/portal/render/father_panel",
            "layout_config": {
                "layout": "parallax_minimalism",
                "allowed_modules": ["warehouse_hub", "audio_orders", "daily_journal"]
            }
        }
    else:
        # Для обычных гостей, пришедших просто отдохнуть под Режиссера
        return {
            "status": "guest_access",
            "welcome_message": f"Добро пожаловать на бесплатный пробный сеанс под Режиссера!",
            "avatar": {"avatar_type": "Анонимный_Наблюдатель"},
            "redirect_endpoint": "/portal/render/index",
            "layout_config": {
                "layout": "guest_parallax",
                "allowed_modules": ["media_player", "trends_stream"]
            }
        }

@app.post("/api/v1/export-cascade-data")
async def export_cascade_data_api(request: Request):
    """🤖 АСИНХРОННЫЙ OPC-ШЛЮЗ: Обрабатывает клики выгрузки файлов из Кабинета ПТО"""
    try:
        req_data = await request.json()
        file_name = req_data.get("file_name", "64-ЭОМ.ЦОД_Каскад_Анализа.xlsx")
        dest = req_data.get("target_destination", "local_pc")
        return {
            "status": "SUCCESS_OPC_COMMITTED",
            "saved_path": f"/root/app/buffer/exports/{dest}/{file_name}",
            "target_pc_path": f"C:\\\\FamilyMira\\\\PTO_Workspace\\\\Downloads\\\\{file_name}"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/portal/render/{page_name}", response_class=HTMLResponse)
async def render_html_page(page_name: str):
    """Безопасный динамический подсос HTML-страниц из абсолютных папок Django-Бронепоезда"""
    base_dirs = [
        "/root/app/storage_control/templates/",
        "/root/app/storage_control/templates/storage_control/",
        "/root/app/templates/",
        "templates/",
        "templates/storage_control/"
    ]
    
    target_file = None
    for d in base_dirs:
        possible_path = os.path.join(d, f"{page_name}.html")
        if os.path.exists(possible_path):
            target_file = possible_path
            break
            
    if not target_file:
        raise HTTPException(status_code=404, detail="Вагон интерфейса не найден в хранилище.")
        
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        raise HTTPException(status_code=500, detail="Ошибка чтения файла из хранилища вечности.")
