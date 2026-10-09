from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Miroha REST Framework", version="79.0")

# Монтируем статику для раздельных файлов CSS и JS
app.mount("/static", StaticFiles(directory="/root/app"), name="static")
templates = Jinja2Templates(directory="/root/app/templates")

# ГЕНЕРАЦИЯ МАТРИЦЫ ИЗ 100 СУВЕРЕННЫХ ТОВАРОВ ПО ПРОЕКТНОМУ СООТНОШЕНИЮ 80/10/10
pin_array = []

# 1. 80% (80 товаров) — Инженерная спецификация чертежей (АР, КМ, ВК, ЭОМ из скриншота)
for i in range(1, 81):
    pin_array.append({
        "host": f"Spec: {00 + i}-АР/КМ",
        "name": f"ИТР-Материал Спецификации №{i} (Швеллер/Труба/Арматура)",
        "price": f"{450 + i*15:,.2f} ₽",
        "logistics": "ТК ПЭК // Деловые Линии",
        "badge_text": "СПЕЦИФИКАЦИЯ 80%",
        "badge_color": "#0d9488"
    })

# 2. 10% (10 товаров) — Расходные запчасти для ИТР и рабочих площадки
for i in range(1, 11):
    pin_array.append({
        "host": f"Host: ИТР-Расходник",
        "name": f"Запчасть/Форма Рабочих №{i} (Каска/Кабель/Бур Bosch Pro)",
        "price": f"1,200.00 ₽",
        "logistics": "ТК СДЭК (1 сутки)",
        "badge_text": "ИТР ЗАПЧАСТИ 10%",
        "badge_color": "#7c3aed"
    })

# 3. 10% (10 товаров) — Партнерский контур рекламы заводов-изготовителей
for i in range(1, 11):
    pin_array.append({
        "host": f"Ad: ПАРТНЕР РФ/КНР",
        "name": f"b2b-Оффер №{i} (Северсталь/Технониколь/Кнауф Маркет)",
        "price": f"Со скидкой API",
        "logistics": "Прямая поставка",
        "badge_text": "РЕКЛАМА ПАРТНЕРОВ 10%",
        "badge_color": "#d97706"
    })

@app.get("/portal/", response_class=HTMLResponse)
async def get_mezzanine_shop(request: Request):
    # Рендерим раздельный HTML-шаблон, передавая массив из 100 товаров
    return templates.TemplateResponse("matrix_mezzanine.html", {"request": request, "pin_array": pin_array})
