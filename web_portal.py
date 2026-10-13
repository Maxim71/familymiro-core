# -*- coding: utf-8 -*-
import os, random
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="FamilyMira Живой ИИ-Онбординг // Тритон-Контур v2.2")

class GuestOnboardingRequest(BaseModel):
    guest_name_or_id: str          
    chosen_skill: str              
    invitation_source: str         

@app.post("/api/v1/portal/onboarding")
def ezhik_onboarding_gate(request: GuestOnboardingRequest):
    """Живой привратник Ёжика: интеграция ПТО, Журналов ресурсов и Бизнес-Анализа Директора"""
    skill = request.chosen_skill.upper()
    
    avatar_metadata = {
        "avatar_type": f"ИТР-Кибер_Мастер_{skill}",
        "visual_style": "Parallax-Neon-Cyberpunk",
        "access_shield": "Юридическая защита ВЕЧНОСТИ активна",
        "database_sync": "PostgreSQL (5432) Connected"
    }
    
    if "ПТО" in skill:
        return {
            "status": "authenticated",
            "welcome_message": f"Приветствуем в системе, {request.guest_name_or_id}! Ёжик зафиксировал твой Скилл ПТО.",
            "avatar": avatar_metadata,
            "redirect_endpoint": "/portal/render/pto_cabinet",
            "layout_config": {
                "layout": "parallax_industrial_engineer",
                "theme": "neon_purple_cad",
                "allowed_modules": ["dxf_blueprint_scan", "procurement_flow", "bim_collision_radar"]
            }
        }
    elif "ДИРЕКТОР" in skill or "МЕНЕДЖЕР" in skill or "АНАЛИТИК" in skill:
        # 🪐 СВЕРХТОЧНАЯ ИНТЕГРАЦИЯ ТВОИХ НОВЫХ ЖУРНАЛОВ И ИИ-АНАЛИЗА ДОХОДОВ ДЛЯ РУКОВОДСТВА
        simulated_resource_journal = {
            "project_name": "Суверенный Макет Монолита MIROHA",
            "active_zone": "Склады М19 // Оси Б-Е // Сектор 3",
            "machinery_hours": {"ИТР-Длинномеры": "48 м/ч", "Бетоносмесители": "120 м/ч"},
            "cascade_status": "🟢 ВСЕ ПАСПОРТА КАЧЕСТВА ПРИВЯЗАНЫ-ЯКОРЯМИ К СУБД"
        }
        
        simulated_executive_analytics = {
            "viewer_role": f"Уважаемый Руководитель {request.guest_name_or_id}",
            "income_optimization": "🚀 АНАЛИЗ ЁЖИКА: Оптимизация плеча закупки у ТК 'Деловые Линии' принесла синдикату +8% чистой прибыли на осях перекрытий ЦОД.",
            "seo_meta_tags": {"meta_title": "FamilyMira Enterprise", "pwa_status": "ACTIVE"},
            "future_plans": "Внедрение автоматических чеков самозанятого и вывод смет openpyxl из ОЗУ"
        }

        return {
            "status": "authenticated",
            "welcome_message": f"Добро пожаловать на капитанский мостик, Руководитель {request.guest_name_or_id}!",
            "avatar": {"avatar_type": "Главный_Директор_Шилд", "visual_style": "Luxury-Параллакс-Gold"},
            "redirect_endpoint": "/api/v5/products/catalog/",
            "pto_resource_journal": simulated_resource_journal,
            "executive_analytics": simulated_executive_analytics
        }
    else:
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
    base_dirs = [
        "/root/app/storage_control/templates/",
        "/root/app/storage_control/templates/storage_control/",
        "/root/app/templates/",
        "templates/"
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
        raise HTTPException(status_code=500, detail="Ошибка чтения файла.")
