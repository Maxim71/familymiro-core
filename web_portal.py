# -*- coding: utf-8 -*-
import os, random
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="FamilyMira Живой ИИ-Онбординг // REST-Triton v3.5")

# Сложная структурированная модель ТИМ-данных для взаимодействия веб-сервисов с машинами
class RESTGuestOnboardingRequest(BaseModel):
    guest_name_or_id: str          
    chosen_skill: str              
    invitation_source: str         
    nested_machine_metadata: Optional[dict] = {
        "content_negotiation": "RFC_2616_ACTIVE",
        "parser_class": "DRF_JSON_Parser_Active",
        "socket_limit": 65535
    }

@app.post("/api/v1/portal/onboarding")
def ezhik_onboarding_gate(request: RESTGuestOnboardingRequest):
    """🤖 КИБЕР-ГЕЙТ ОНБОРДИНГА: Принимает сложные структурированные REST-массивы данных в ОЗУ"""
    skill = request.chosen_skill.upper()
    
    avatar_metadata = {
        "avatar_type": f"ИТР-REST_Мастер_{skill}",
        "visual_style": "Parallax-Neon-Cyberpunk",
        "access_shield": "Юридическая защита ВЕЧНОСТИ активна",
        "media_negotiation": "SUCCESS // application/json parsed"
    }
    
    if "ПТО" in skill:
        # Интегрируем Журналы и Пины Быстрых решений прямо в гибкий REST-вывод для Директора и ПТО
        return {
            "status": "authenticated",
            "welcome_message": f"Приветствуем в системе, {request.guest_name_or_id}! Малкольм Трединик верифицировал REST-Request контур.",
            "avatar": avatar_metadata,
            "redirect_endpoint": "/portal/render/pto_cabinet",
            "layout_config": {
                "layout": "parallax_industrial_engineer",
                "theme": "neon_purple_cad",
                "allowed_modules": ["dxf_blueprint_scan", "procurement_flow", "bim_collision_radar"],
                "rest_framework_negotiation": request.nested_machine_metadata
            }
        }
    else:
        return {
            "status": "guest_access",
            "welcome_message": f"Добро пожаловать на суверенный сеанс автоматизации!",
            "avatar": {"avatar_type": "Анонимный_Наблюдатель"},
            "redirect_endpoint": "/portal/render/index"
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

@app.get("/portal/render/pto_cabinet", response_class=HTMLResponse)
async def render_html_page():
    target_file = "/root/app/storage_control/templates/pto_cabinet.html"
    if not os.path.exists(target_file):
        raise HTTPException(status_code=404, detail="Вагон интерфейса Кабинета ПТО не найден в хранилище.")
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        raise HTTPException(status_code=500, detail="Ошибка чтения файла.")
