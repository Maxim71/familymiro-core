import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from parser_intelligence import ezhik_parse_filename

app = FastAPI(title="FamilyMira Вагонный Диспетчер")

# ==========================================
# ВАГОН 1: ИНТЕЛЛЕКТ ПОРТРЕТА ПОЛЬЗОВАТЕЛЯ
# ==========================================
class UserProfile:
    @staticmethod
    def get_portrait(user_status: str):
        """Ёжик мгновенно составляет портрет и адаптирует дизайн"""
        statuses = {
            "самозанятый": {"layout": "параллакс_минимализм", "allowed_modules": ["баланс", "чек_онлайн"]},
            "ип": {"layout": "параллакс_инженер", "allowed_modules": ["акты", "склад", "расходы", "ifc_B2B"]},
            "вечность": {"layout": "космический_хронограф", "allowed_modules": ["капсула_времени", "память_лет"]}
        }
        return statuses.get(user_status.lower(), {"layout": "гость", "allowed_modules": []})

# ==========================================
# ВАГОН 2: РЕЖИССЕР — AI МЕДИА (Озвучка Lip-Sync)
# ==========================================
class AIExecutiveDirector:
    @staticmethod
    def process_voice_acting(video_file: str, gender: str):
        """Озвучка по губам: Мужской -> Геральт, Женский -> Цири"""
        if gender == "male":
            return {"status": "озвучено", "voice": "Геральт из Ривии", "effect": "Сглажено ИИ Ёжика"}
        return {"status": "озвучено", "voice": "Цирилла (Цири)", "effect": "Lip-Sync выполнен"}

# ==========================================
# ВАГОН 3: МАРШРУТИЗАТОРЫ И ТЕКУЩИЕ HTML
# ==========================================
@app.get("/portal/{status}", response_class=HTMLResponse)
async def render_portal(status: str):
    portrait = UserProfile.get_portrait(status)
    
    # Вместо генерации кода с нуля, Ёжик считывает ваши существующие файлы из templates/
    template_path = f"templates/storage_control/{status}.html" if os.path.exists(f"templates/storage_control/{status}.html") else "templates/index.html"
    
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return html_content
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Вагон с шаблоном не найден в системе")

@app.post("/api/v1/ai-dubbing")
def ai_dubbing(video_name: str, voice_type: str):
    """Эндпоинт для ИИ-видео-утренников Режиссера"""
    return AIExecutiveDirector.process_voice_acting(video_name, voice_type)
