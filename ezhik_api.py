from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn
from parser_intelligence import ezhik_parse_filename

app = FastAPI(title="Miroha B2B OPC-API Контур + Магазин Пинов")

class DrawingRequest(BaseModel):
    filename: str
    pin_code: Optional[str] = None # Новое поле для интеграции магазина пинов

@app.post("/api/v1/parse-drawing")
def parse_drawing(request: DrawingRequest):
    if not request.filename:
        raise HTTPException(status_code=400, detail="Имя файла пустое")
        
    # Передаем имя файла и пин-код в интеллект Ёжика
    analysis = ezhik_parse_filename(request.filename, request.pin_code)
    return analysis

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8050)
