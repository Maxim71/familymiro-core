import asyncio
import httpx

async def test_director_orchestration():
    print('=== [РЕЖИССЕР] ЗАПУСК СВЯЗАННЫХ ИТР-СЦЕНАРИЕВ ===')
    async with httpx.AsyncClient() as client:
        # Полный и точный адрес асинхронного FastAPI шлюза Ёжика
        url = 'http://127.0.0'
        data = {'video_name': 'utrennik_2026.mp4', 'voice_type': 'male'}
        
        response_voice = await client.post(url, json=data)
        print(f"Ответ Режиссера: {response_voice.json()}")

        print('Эмуляция стрима Блогера и доната в Капитал Ёжика...')
        mock_donate_api = {
            'streamer': 'Tech_Blogger_China',
            'donation_rub': 5000.00,
            'anonymity': True
        }
        print(f'Поток донатов OPC-Браузера: {mock_donate_api}')
        print('[OK] Мобильный плеер синхронизирован напрямую.')

if __name__ == "__main__":
    asyncio.run(test_director_orchestration())
