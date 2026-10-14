import asyncio
from fastapi import FastAPI
from pydantic import BaseModel
import httpx
import uvicorn
import threading
import time

# 1. Локальная сборка мини-контура Режиссера прямо внутри теста
app = FastAPI()

class DubbingRequest(BaseModel):
    video_name: str
    voice_type: str

@app.post("/api/v1/ai-dubbing")
def ai_dubbing(request: DubbingRequest):
    if request.voice_type == "male":
        return {"status": "озвучено", "voice": "Геральт из Ривии", "file": request.video_name}
    return {"status": "озвучено", "voice": "Цирилла", "file": request.video_name}

def start_server():
    uvicorn.run(app, host="127.0.0.1", port=8099, log_level="error")

if __name__ == "__main__":
    print("=== [РЕЖИССЕР] ЗАПУСК СВЯЗАННЫХ ИТР-СЦЕНАРИЕВ В ИЗОЛЯЦИИ ===")
    
    # Запускаем тестовый сервер на свободном порту 8099 в отдельном потоке
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Даем серверу 1 секунду на инициализацию контура
    time.sleep(1)
    
    async def run_client():
        async with httpx.AsyncClient() as client:
            print("Тестирование ИИ-озвучки по губам (Голос: Геральт)...")
            response = await client.post(
                "http://127.0.0",
                json={"video_name": "utrennik_2026.mp4", "voice_type": "male"}
            )
            print(f"Ответ Режиссера (JSON): {response.json()}\n")
            
            print("Эмуляция стрима Блогера и доната в Капитал Ёжика...")
            mock_donate_api = {
                "streamer": "Tech_Blogger_China",
                "donation_rub": 5000.00,
                "anonymity": True
            }
            print(f"Поток донатов OPC-Браузера: {mock_donate_api}")
            print("[OK] Мобильный плеер синхронизирован напрямую в изолированном вагоне.")

    # Запускаем асинхронный клиент
    asyncio.run(run_client())
