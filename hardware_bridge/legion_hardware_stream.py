import asyncio
import aiohttp
import sys

async def main():
    print("🛰️  [PYTHON HARDWARE BRIDGE]: Контур контроллеров БСУ запущен...")
    client_id = "CID-2026-99"
    captured_weight_tons = 45.85
    
    # Скрипт ломится напрямую в наш FastAPI Docker-шлюз на приватной сети
    url = "http://192.168.0"
    data = {"client_id": client_id, "vor_value": str(captured_weight_tons)}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, timeout=2) as response:
                res_text = await response.text()
                print(f"✅ [ВЫСТРЕЛ В PostgreSQL УСПЕШЕН]: {res_text}")
    except Exception as e:
        print(f"❌ [КЛИНЧ ПРИВАТНОЙ СЕТИ]: {e}")

if __name__ == '__main__':
    asyncio.run(main())
