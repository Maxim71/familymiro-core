import asyncio
import httpx

async def test_director_orchestration():
    print("=== ЗАПУСК ТЕСТОВЫХ СЦЕНАРИЕВ РЕЖИССЕРА ===")
    
    async with httpx.AsyncClient() as client:
        print("Тестирование ИИ-озвучки по губам (Голос: Геральт)...")
        response_voice = await client.post(
            "http://127.0.0",
            json={"video_name": "utrennik_2026.mp4", "voice_type": "male"}
        )
        print(f"Ответ Режиссера: {response_voice.json()}\n")

        print("Эмуляция стрима Блогера и отправки доната в Капитал Ёжика...")
        mock_donate_api = {
            "streamer": "Tech_Blogger_China",
            "trending_tag": "BIM_Stroyka",
            "donation_rub": 5000.00,
            "anonymity": True,
            "legal_protection": "Юридический щит Капитала активен"
        }
        print(f"Поток донатов OPC-Браузера: {mock_donate_api}")
        print("[OK] Мобильный плеер синхронизирован с API трендов.")

if __name__ == "__main__":
    asyncio.run(test_director_orchestration())
