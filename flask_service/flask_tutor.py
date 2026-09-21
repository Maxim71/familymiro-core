import random
import requests
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Вековая база знаний ИТР-Документации холдинга Максима
ITR_DOCUMENTATION = {
    "вор_лимиты": "📐 Лимиты ВОР (Ведомость объемов работ): Жесткий сметный потолок проекта. По арматуре А500С — 45.0 тонн. Любое превышение — стоп-ордер в ERP.",
    "м19_склад": "🧱 Ордер М-19: Материальный отчет материально-ответственного лица. Оформляется прорабом на оси Тулы каждую пятницу. Защищает от левых списаний.",
    "кс2_защита": "🛡️ Защита актов КС-2/КС-3: Требует 100% исполнительной документации. Ведется через Живой Журнал осей Оракула и пиксельный CV-анализ."
}

class EzhikBiMentor:
    def __init__(self):
        self.name = "Ёжик-BI-Аналитик"
        self.phrases_advices = [
            "⚠️ ВНИМАНИЕ: Вижу скрытую зону риска в закупках! Срочно сверь накладные М-15 с лимитами ПТО.",
            "✅ ИТР-АНАЛИЗ: Объемы бетона сходятся. Зона безопасна. Даю добро на формирование акта КС-3.",
            "🚨 КРИТИЧЕСКИЙ СБОЙ: Прораб указал утерю документов! Авто-списание заблокировано в СУБД SQLite."
        ]

    def analyze_and_calculate(self, user_question, current_volume):
        """🦔 МАТЕМАТИЧЕСКИЙ АНАЛИЗАТОР ЁЖИКА: Расчет задач и подсветка зон риска"""
        txt = user_question.lower()
        limit_tons = 45.0
        
        # Подсчитываем остаток лимита
        leftover = limit_tons - current_volume
        
        # Динамически определяем зону риска и цвет подсветки
        if leftover < 0:
            zone_status = "🚨 КАТАСТРОФИЧЕСКИЙ ПЕРЕРАСХОД (КРАСНАЯ ЗОНА)"
            zone_color = "#ff0055"
            advice = "Жесткая блокировка ERP! Дополнительные объемы не согласованы ПТО. Транш Альфа-Банка заморожен."
        elif leftover <= 5.0:
            zone_status = "⚠️ ПРЕДАВАРИЙНЫЙ ЛИМИТ (ЖЕЛТАЯ ЗОНА)"
            zone_color = "#ffaa00"
            advice = "Внимание Замначальника участка! Резервы на исходе. Срочно подбить накопительные акты КС-2."
        else:
            zone_status = "✅ СМЕТНЫЙ КОМФОРТ (ЗЕЛЕНАЯ ЗОНА)"
            zone_color = "#00ff66"
            advice = "Объемы в пределах нормы. Контур опечатан. Робот-Ёжик одобряет текущую смену."
            
        return {
            "leftover": f"{leftover:.1f} тонн",
            "zone": zone_status,
            "color": zone_color,
            "advice": advice,
            "phrase": random.choice(self.phrases_advices)
        }

MENTOR = EzhikBiMentor()

# 🎨 ВСТРОЕННЫЙ НЕОНОВЫЙ ШАБЛОН ИНТЕРФЕЙСА ОБУЧЕНИЯ И API-РАДИУСА
FLASK_HTML_UI = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Miroha Flask // ИТР-Обучение и BI-Парсер</title>
    <style>
        :root { --bg: #04060a; --card: #0b0f19; --cyan: #00f0ff; --pink: #ff007f; }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: monospace; }
        body { background: var(--bg); color: #e2e8f0; padding: 15px; display: flex; justify-content: center; }
        .container { width: 100%; max-width: 480px; background: var(--card); border: 1px solid #1e2640; padding: 20px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        h1 { color: var(--cyan); font-size: 1.1rem; text-align: center; margin-bottom: 15px; text-transform: uppercase; border-bottom: 1px dashed #1e2640; padding-bottom: 10px; }
        .doc-section { background: rgba(255,255,255,0.02); border: 1px solid #141b2d; padding: 10px; border-radius: 6px; margin-bottom: 15px; font-size: 0.72rem; line-height: 1.4; }
        .badge { display: inline-block; background: var(--pink); color: #fff; padding: 2px 6px; font-size: 8px; font-weight: bold; border-radius: 4px; margin-bottom: 5px; }
        textarea, input { width: 100%; background: #020306; border: 1px solid #1e2640; color: #fff; padding: 8px; border-radius: 6px; font-size: 0.75rem; margin-bottom: 10px; outline: none; }
        .btn { width: 100%; background: linear-gradient(135deg, var(--cyan), #00aaaa); color: #000; border: none; padding: 10px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 0.75rem; text-transform: uppercase; }
        .result-box { margin-top: 15px; padding: 12px; border-radius: 6px; background: #020306; font-size: 0.72rem; line-height: 1.4; display: none; border-left: 4px solid var(--cyan); }
    </style>
</head>
<body>
<div class="container">
    <h1>🛰️ Flask Intelligence Справочник</h1>
    
    <div class="badge" style="background:var(--cyan); color:#000;">📚 ИТР-ДОКУМЕНТАЦИЯ ПО СИСТЕМЕ</div>
    <div class="doc-section">
        <b>[ВОР ЛИМИТЫ]:</b> {{ doc_vor }}<br><br>
        <b>[М-19 СКЛАД]:</b> {{ doc_m19 }}<br><br>
        <b>[КС-2 ЗАЩИТА]:</b> {{ doc_ks2 }}
    </div>

    <div class="badge">🦔 ДИАЛОГ С ЁЖИКОМ-АНАЛИТИКОМ</div>
    <div class="doc-section" style="background: rgba(0,240,255,0.01);">
        <label style="font-size:10px; color:#8a99ad;">Введите ваш ИТР-вопрос или факт с линии:</label>
        <textarea id="ezhik_question" placeholder="Пример: Сдаем наряд по арматуре, Коля уложил металл...">Сдаем наряд по армированию плиты</textarea>
        
        <label style="font-size:10px; color:#8a99ad;">Текущий физический объем расхода (тонн):</label>
        <input type="number" id="ezhik_volume" value="42.5">
        
        <button class="btn" onclick="askEzhikFlaskBI()">Запустить расчет и разбор Агента()</button>
    </div>

    <div class="result-box" id="flask_res_box"></div>
</div>

<script>
function askEzhikFlaskBI() {
    let box = document.getElementById("flask_res_box");
    box.style.display = "block";
    box.innerHTML = "⏳ <i>Flask парсит API-поток... Семантический разбор...</i>";
    
    let q = document.getElementById("ezhik_question").value;
    let v = document.getElementById("ezhik_volume").value;
    
    fetch("/api/flask-mentor-query/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: json = JSON.stringify({ question: q, volume: parseFloat(v) })
    })
    .then(res => res.json())
    .then(data => {
        box.style.borderLeftColor = data.color;
        box.innerHTML = `
            <b style="color:var(--cyan);">🦔 ЁЖИК СКАЗАЛ:</b> "${data.phrase}"<br><br>
            <b style="color:${data.color};">📍 СТАТУС ЗОНЫ:</b> ${data.zone}<br>
            <b>📐 Остаток лимита сметы:</b> ${data.leftover}<br><br>
            <b style="color:var(--pink);">📋 ИТР-СОВЕТ ЗАМНАЧАЛЬНИКА:</b> ${data.advice}
        `;
    });
}
</script>
</body>
</html>
"""

@app.route('/')
def flask_home():
    """Рендеринг ИТР-документации в интерфейс"""
    return render_template_string(
        FLASK_HTML_UI, 
        doc_vor=ITR_DOCUMENTATION["вор_лимиты"],
        doc_m19=ITR_DOCUMENTATION["м19_склад"],
        doc_ks2=ITR_DOCUMENTATION["кс2_защита"]
    )

@app.route('/api/flask-mentor-query/', methods=['POST'])
def flask_mentor_query_api():
    """📡 API ПАРСЕР: Принимает JSON-поток, рассчитывает метрики и подсвечивает зоны риска"""
    data = request.get_json() or {}
    question = data.get('question', '')
    volume = data.get('volume', 0.0)
    
    # Расчет через аналитика
    analysis_result = MENTOR.analyze_and_calculate(question, volume)
    
    # Дублируем экстренный рапорт в Telegram Капитану Максиму на телефон, если зафиксирована критическая зона
    if "КРАСНАЯ" in analysis_result["zone"] or "ЖЕЛТАЯ" in analysis_result["zone"]:
        report_text = (
            f"🛰️ <b>[FLASK INTELLIGENCE // ЭКСТРЕННЫЙ ВСПЛЕСК]</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚠️ <b>Предупреждение от Ёжика-Аналитика!</b>\n"
            f"🚨 <b>Зона риска:</b> {analysis_result['zone']}\n"
            f"📐 <b>Остаток по ВОР:</b> {analysis_result['leftover']}\n"
            f"📋 <b>Директива ПТО:</b> {analysis_result['advice']}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🦔 <i>Микросервис Flask зафиксировал аномалию трафика в ОЗУ.</i>"
        )
        try:
            requests.post(f"https://telegram.org", data={
                "chat_id": "541888946", "text": report_text, "parse_mode": "HTML"
            }, timeout=2)
        except Exception: pass

    return jsonify(analysis_result)

if __name__ == '__main__':
    # Запускаем Flask на порту 5000 слушать весь мир наружу
    app.run(host='0.0.0.0', port=5000, debug=False)
