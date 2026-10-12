from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn
from parser_intelligence import ezhik_parse_filename, ezhik_warehouse_audit

app = FastAPI(
    title="FamilyMira Промышленный API-Контур",
    description="Параллельный микросервис автоматизации рутины ИТР и магазина пинов"
)

class DrawingRequest(BaseModel):
    filename: str
    pin_code: Optional[str] = None

@app.post("/api/v1/parse-drawing")
def parse_drawing(request: DrawingRequest):
    if not request.filename:
        raise HTTPException(status_code=400, detail="Имя файла не передано")
        
    # Шаг 1: Парсим файл и извлекаем ИТР-объемы
    analysis = ezhik_parse_filename(request.filename, request.pin_code)
    
    # Шаг 2: Если шифр распознан, автоматически проводим аудит склада ("Зрение Сокола")
    if analysis["status"] == "success":
        cipher = analysis["structural_data"]["cipher"]
        warehouse_status = ezhik_warehouse_audit(cipher)
        analysis["warehouse_intelligence"] = warehouse_status
        
    return analysis

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8050)

@app.post("/api/v1/global-orchestration")
def global_orchestration(target: str):
    from parser_intelligence import ezhik_global_search
    return ezhik_global_search(target)
