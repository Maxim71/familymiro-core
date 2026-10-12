from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn
from parser_intelligence import ezhik_parse_filename, ezhik_warehouse_audit

app = FastAPI(title="FamilyMira Промышленный API-Контур + РЕЖИССЕР")

class DrawingRequest(BaseModel):
    filename: str
    pin_code: Optional[str] = None

class DubbingRequest(BaseModel):
    video_name: str
    voice_type: str

@app.post("/api/v1/parse-drawing")
def parse_drawing(request: DrawingRequest):
    if not request.filename:
        raise HTTPException(status_code=400, detail="Имя файла пустое")
    analysis = ezhik_parse_filename(request.filename, request.pin_code)
    if analysis["status"] == "success":
        cipher = analysis["structural_data"]["cipher"]
        analysis["warehouse_intelligence"] = ezhik_warehouse_audit(cipher)
    return analysis

@app.post("/api/v1/ai-dubbing")
def ai_dubbing(request: DubbingRequest):
    if request.voice_type == "male":
        return {"status": "озвучено", "voice": "Геральт из Ривии", "file": request.video_name}
    return {"status": "озвучено", "voice": "Цирилла", "file": request.video_name}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8050)


class FinanceRequest(BaseModel):
    authenticated: bool
    status: str
    balance: float

@app.post("/api/v1/neuro-radar-finance")
def get_radar_finance(request: FinanceRequest):
    from parser_intelligence import ezhik_neuro_radar_financials
    return ezhik_neuro_radar_financials(request.authenticated, request.status, request.balance)
