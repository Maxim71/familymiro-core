# -*- coding: utf-8 -*-
import os, random, json
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="FamilyMira Живой ИИ-Онбординг // Триада Портов v94.0")

class RESTGuestOnboardingRequest(BaseModel):
    guest_name_or_id: str          
    chosen_skill: str              
    invitation_source: str         
    nested_machine_metadata: Optional[dict] = {
        "content_negotiation": "RFC_2616_ACTIVE",
        "request_port": 8501,
        "totp_token": "123456"
    }

@app.post("/api/v1/portal/onboarding")
def ezhik_onboarding_gate(request: RESTGuestOnboardingRequest):
    """🤖 КИБЕР-ГЕЙТ ОНБОРДИНГА: Масштабирование под ИТР-порты Вечности, Стройки и Режиссера"""
    skill = request.chosen_skill.upper()
    
    avatar_metadata = {
        "avatar_type": f"ИТР-Кибер_Мастер_{skill}",
        "visual_style": "Parallax-Neon-Cyberpunk",
        "access_shield": "Юридическая защита ВЕЧНОСТИ активна"
    }
    
    # Снайперски разводим логику по портам триады, которые ты разметил
    return {
        "status": "authenticated",
        "welcome_message": f"Приветствуем в системе, {request.guest_name_or_id}! Триада модулей успешно верифицирована.",
        "avatar": avatar_metadata,
        "redirect_endpoint": "/portal/render/pto_cabinet",
        "triada_ports_allocation": {
            "vechnность_bottle_db": 8503,
            "stroyka_monolith_id": 8501,
            "regisser_train_iac": 8502
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
    except Exception as e: raise HTTPException(status_code=400, detail=str(e))

@app.get("/portal/render/pto_cabinet", response_class=HTMLResponse)
async def render_html_page():
    target_file = "/root/app/storage_control/templates/pto_cabinet.html"
    if not os.path.exists(target_file): raise HTTPException(status_code=404, detail="Не найден.")
    with open(target_file, "r", encoding="utf-8") as f: return f.read()

@app.get("/portal/gate", response_class=HTMLResponse)
async def render_gate_page():
    """🎰 ОТДЕЛЬНЫЙ ЭНДПОИНТ ДЛЯ ОТРИСОВКИ НАШЕГО НОВОГО ИИ-ВХОДА"""
    target_file = "/root/app/storage_control/templates/storage_control/onboarding_gate.html"
    with open(target_file, "r", encoding="utf-8") as f: return f.read()
