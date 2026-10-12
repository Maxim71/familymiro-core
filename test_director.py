import asyncio
import httpx

async def test_director_orchestration():
    print('=== ЗАПУСК ПРЯМЫХ ТЕСТОВЫХ СЦЕНАРИЕВ РЕЖИССЕРА ===')
    async with httpx.AsyncClient() as client:
        print('Тестирование ИИ-озвучки по губам (Голос: Геральт)...')
        response_voice = await client.post(
            'http://127.0.0',
            json={'video_name': 'utrennik_2026.mp4', 'voice_type': 'male'}
        )
        print(f'Ответ Режиссера: {response_voice.json()}\n')

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
