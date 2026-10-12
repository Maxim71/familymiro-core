from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from parser_intelligence import ezhik_parse_filename

# Инициализируем промышленный узел связи Ёжика (OPC / API)
app = FastAPI(
    title="Miroha B2B OPC-API Контур",
    description="Строительный интеллект Ёжика (Модуль: РЕЖИССЕР / СТРОЙКА)",
    version="1.0.0"
)

# Модель входящего запроса от прораба или внешней системы
class DrawingRequest(BaseModel):
    filename: str

@app.get("/")
def read_root():
    return {
        "status": "online",
        "engine": "OpenAI Triton Custom Layer",
        "adapter": "FastAPI/OPC-Link",
        "message": "Ёжик слушает эфир и готов разбирать чертежи."
    }

@app.post("/api/v1/parse-drawing")
def parse_drawing(request: DrawingRequest):
    """Эндпоинт промышленного обмена: принимает имя чертежа, выдает ИТР-аналитику"""
    if not request.filename:
        raise HTTPException(status_code=400, detail="Имя файла пустое")
        
    analysis = ezhik_parse_filename(request.filename)
    return analysis

if __name__ == "__main__":
    # Запускаем внутренний шлюз на порту 8050 (чтобы не занимать порты Django 8000)
    uvicorn.run(app, host="127.0.0.1", port=8050)
