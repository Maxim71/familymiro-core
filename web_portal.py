import os
import sys
import django
from flask import Flask, render_template_string

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()

from storage_control.models import ConstructionAnalytics

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>FAMILYMIRO — Монитор Хозяина</title>
    <style>
        body { font-family: 'Courier New', monospace; background: #0b0f19; color: #f1f5f9; padding: 40px; text-align: center; }
        .dashboard { max-width: 700px; margin: 0 auto; background: #1e293b; padding: 30px; border-radius: 8px; border: 1px solid #334155; box-shadow: 0 0 20px rgba(56, 189, 248, 0.1); }
        h1 { color: #38bdf8; border-bottom: 1px solid #334155; padding-bottom: 15px; font-size: 22px; letter-spacing: 1px; }
        .card { background: #0f172a; padding: 20px; margin: 20px 0; border-radius: 6px; border-left: 4px solid #10b981; text-align: left; }
        .risk { border-left: 4px solid #ef4444; background: #451a03; }
        .amount { font-weight: bold; color: #10b981; }
        .btn-download { display: inline-block; background: #3b82f6; color: #fff; padding: 10px 20px; text-decoration: none; font-weight: bold; border-radius: 4px; margin-top: 15px; font-size: 13px; }
    </style>
</head>
<body>
    <div class="dashboard">
        <h1>🏗️ СТРОИТЕЛЬНЫЙ МОНИТОР — FAMILYMIRO 1.0</h1>
        <p style="color: #94a3b8; font-size: 13px;">— Автономный шлюз на Flask (Данные из Postgres) —</p>
        
        {% for project in projects %}
        <div class="card {% if project.is_risk_detected %}risk{% endif %}">
            <h3 style="margin-top: 0; color: #f8fafc;">Объект: {{ project.project_name }}</h3>
            <p>Общая смета: <span class="amount">{{ project.total_budget }} руб.</span></p>
            <p>Текущие расходы: <strong>{{ project.current_expenses }} руб.</strong></p>
            <p><strong>ИИ-Анализ сметы:</strong> <span style="color: #f43f5e;">{{ project.analysis_summary }}</span></p>
            {% if project.presentation_pdf %}
                <a href="/media/reports/report_project_{{ project.id }}.pdf" class="btn-download" download>📥 Скачать ИИ-Презентацию (PDF)</a>
            {% endif %}
        </div>
        {% else %}
        <p style="color: #94a3b8; padding: 30px 0;">Активных строительных объектов на бюджетировании пока нет.<br>Запустите скрипт auditor.py для генерации данных.</p>
        {% endfor %}
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    projects = ConstructionAnalytics.objects.all()
    return render_template_string(HTML_TEMPLATE, projects=projects)

if __name__ == '__main__':
    print("🚀 Автономный веб-портал Flask запущен...")
    app.run(debug=True, port=5000)
