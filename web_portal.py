import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="FamilyMira Живой ИИ-Онбординг")

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

@app.get("/portal/render/{page_name}", response_class=HTMLResponse)
async def render_html_page(page_name: str):
    """Безопасный динамический подсос HTML-страниц из templates/"""
    target_file = f"templates/{page_name}.html"
    if not os.path.exists(target_file):
        target_file = f"templates/storage_control/{page_name}.html"
        
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Вагон интерфейса не найден в хранилище.")
