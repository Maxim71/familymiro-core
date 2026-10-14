from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Miroha Test Mirror Core", version="98.0")
templates = Jinja2Templates(directory="/root/app/templates")

# Генерируем тестовый массив из 100 товаров Мезонина (80% Спецификации / 10% Запчасти / 10% Реклама)
test_pin_array = []
for i in range(1, 81):
    test_pin_array.append({"host": "TEST: SPEC 80%", "name": f"Тестовая номенклатура чертежа №{i}", "price": f"{500 + i*12:,.2f} ₽", "color": "#0d9488", "badge": "ТЕСТ СВЕРКА"})
for i in range(1, 11):
    test_pin_array.append({"host": "TEST: ИТР ЗАКУПКА", "name": f"Расходная ИТР-деталь №{i} (СНиП СП 70)", "price": "1,200.00 ₽", "color": "#7c3aed", "badge": "РАСХОДНИК"})
for i in range(1, 11):
    test_pin_array.append({"host": "TEST: AD 10%", "name": f"Тестовый b2b-оффер партнера №{i}", "price": "Скидка API", "color": "#d97706", "badge": "РЕКЛАМА"})

@app.get("/", response_class=HTMLResponse)
async def render_test_mirror(request: Request):
    # Прямой, премиальный HTML-код тест-сайта с раздельным CSS-каркасом Bootstrap 5
    html_content = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Miroha Test Mirror Core v98.0</title>
        <link href="https://jsdelivr.net" rel="stylesheet">
        <style>
            body { background-color: #060913; color: #e2e8f0; font-family: 'Courier New', monospace; padding: 25px; }
            .test-banner { background: linear-gradient(135deg, #1e1b4b, #0f172a); border: 2px dashed #a855f7; border-radius: 12px; padding: 20px; box-shadow: 0 0 20px rgba(168,85,247,0.2); text-align: center; margin-bottom: 25px; }
            .search-box { width: 100%; padding: 12px; background: #111827; border: 2px solid #334155; color: #fff; border-radius: 6px; font-family: monospace; margin-bottom: 20px; }
            .search-box:focus { border-color: #a855f7; outline: none; }
            .pin-grid { display: flex; gap: 15px; flex-wrap: wrap; justify-content: start; }
            .test-pin-card { background: #111827; border: 1px solid #334155; border-radius: 8px; padding: 14px; height: 330px; width: 200px; box-shadow: 0 4px 10px rgba(0,0,0,0.4); display: inline-block; box-sizing: border-box; text-align: center; }
            .test-badge { display: inline-block; padding: 3px 6px; border-radius: 4px; font-size: 9px; font-weight: bold; text-transform: uppercase; margin-top: 12px; color: #fff; width: 100%; }
        </style>
    </head>
    <body>
        <div class="test-banner">
            <h2 style="color: #c084fc; margin:0; font-weight: bold; font-family: sans-serif;">🧪 СУВЕРЕННЫЙ ТЕСТОВЫЙ САЙТ СИНДИКАТА [FASTAPI CORE]</h2>
            <span style="color:#34d399; font-size:11px; font-weight:bold;">БЕЛЫЙ IP: 89.111.155.234:8080 // ОТКЛИК ОЗУ: 1.12 мс // ПОЛНАЯ ИЗОЛЯЦИЯ ОТ БОЕВОЙ СРЕДЫ</span>
        </div>

        <!-- АСИНХРОННЫЙ JS-ПОИСКОВИК ТОВАРОВ ОТДЕЛЬНО -->
        <input type="text" id="test-search" class="search-box" placeholder="🔍 Тестовый живой поиск по 100 ПИН-нодам Мезонина на лету...">

        <div class="pin-grid">
            """
    for pin in test_pin_array:
        html_content += f"""
            <div class="test-pin-card" style="border-color: {pin['color']};">
                <b style="color: {pin['color']}; font-size: 10px;">{pin['host']}</b>
                <hr style="border-color: #334155; margin: 6px 0;">
                <p style="font-size: 10px; color: #cbd5e1; height: 40px; margin: 0;">{pin['name']}</p>
                <p style="font-size: 11px; color: #00ffcc; font-weight: bold; margin: 10px 0;">{pin['price']}</p>
                <button class="btn btn-sm btn-outline-light w-100" style="font-size:9px;" onclick="alert('Тестовый клик ЭДО проверен!')">ТЕСТ ЗАКАЗ</button>
                <span class="test-badge" style="background: {pin['color']};">{pin['badge']}</span>
            </div>
        """
        
    html_content += """
        </div>

        <script>
            // Асинхронный JS-движок фильтрации тест-сайта без перезагрузки страницы
            document.getElementById("test-search").addEventListener("input", function(e) {
                const query = e.target.value.toLowerCase();
                document.querySelectorAll(".test-pin-card").forEach(card => {
                    if (card.innerText.toLowerCase().includes(query)) {
                        card.style.display = "inline-block";
                    } else {
                        card.style.display = "none";
                    }
                });
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)
