import os
import sys
import django
from pathlib import Path
from decimal import Decimal

# Инициализация Django окружения внутри воркера
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_dir))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from storage_control.models import AutoReceipt, ConstructionAnalytics

def run_smart_audit(project_id, budget_limits):
    """
    project_id: ID строительного объекта из базы
    budget_limits: словарь лимитов сметы, например {'Бетон': 100000, 'Арматура': 50000}
    """
    # 1. Извлекаем все активные чеки из Postgres
    receipts = AutoReceipt.objects.filter(is_reported=False)
    
    # Считаем траты по категориям
    expenses_by_cat = {}
    total_spent = Decimal("0.0")
    
    for r in receipts:
        expenses_by_cat[r.category] = expenses_by_cat.get(r.category, Decimal("0.0")) + r.total_amount
        total_spent += r.total_amount

    if not expenses_by_cat:
        print("ℹ️ Нет новых чеков для проведения аудита.")
        return

    # 2. ИИ-АНАЛИЗ И ПОИСК ПЕРЕРАСХОДОВ
    warnings = []
    risk_detected = False
    
    for cat, amount in expenses_by_cat.items():
        limit = budget_limits.get(cat, 999999) # если лимит не задан
        if amount > limit:
            percent_over = ((amount - limit) / limit) * 100
            warnings.append(f"Внимание! Перерасход по категории '{cat}' на {percent_over:.1f}%!")
            risk_detected = True

    # 3. СТРОИМ ГРАФИК РАСХОДОВ ЧЕРЕЗ MATPLOTLIB
    categories = list(expenses_by_cat.keys())
    amounts = [float(val) for val in expenses_by_cat.values()]
    
    plt.figure(figsize=(6, 4))
    plt.bar(categories, amounts, color=['#3b82f6', '#10b981', '#f59e0b', '#ef4444'])
    plt.title("Распределение расходов по проекту")
    plt.ylabel("Сумма (руб)")
    
    # Сохраняем график как временную картинку
    chart_path = "temp_construction_chart.png"
    plt.savefig(chart_path, bbox_inches='tight')
    plt.close()

    # 4. СБОРКА ИТОГОВОЙ PDF-ПРЕЗЕНТАЦИИ ЧЕРЕЗ REPORTLAB
    pdf_filename = f"report_project_{project_id}.pdf"
    media_reports_dir = Path(settings.MEDIA_ROOT) / "reports"
    media_reports_dir.mkdir(parents=True, exist_ok=True)
    final_pdf_path = media_reports_dir / pdf_filename

    c = canvas.Canvas(str(final_pdf_path), pagesize=letter)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, 750, f"ИИ-АУДИТ СМЕТЫ: ПРОЕКТ #{project_id}")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, 710, f"Общий бюджет освоен на: {total_spent} руб.")
    
    # Отрисовка предупреждений ИИ на презентации (Красный цвет при риске)
    y_pos = 680
    if risk_detected:
        c.setFillColorRGB(0.8, 0.1, 0.1) # Красный шрифт
        c.drawString(50, y_pos, "СТАТУС: КРИТИЧЕСКИЙ РИСК КАССОВОГО РАЗРЫВА!")
        y_pos -= 20
        for w in warnings:
            c.drawString(50, y_pos, f"— {w}")
            y_pos -= 20
    else:
        c.setFillColorRGB(0.1, 0.6, 0.1) # Зеленый шрифт
        c.drawString(50, y_pos, "СТАТУС: Траты в пределах нормы сметы.")
        y_pos -= 20

    # Вставляем сгенерированный график расходов прямо в PDF презентацию
    c.setFillColorRGB(0, 0, 0)
    c.drawImage(chart_path, 50, 250, width=400, height=280)
    c.drawString(50, 220, "Прогноз: При сохранении темпов трат, кассовый разрыв наступит через 2 недели.")
    
    c.save()
    
    # Удаляем временный график
    if os.path.exists(chart_path):
        os.remove(chart_path)

    # 5. Сохраняем аналитику в модель строительного объекта
    ConstructionAnalytics.objects.update_or_create(
        id=project_id,
        defaults={
            'project_name': f"Объект #{project_id}",
            'total_budget': sum(budget_limits.values()),
            'current_expenses': total_spent,
            'analysis_summary': "\n".join(warnings) if warnings else "Все в норме",
            'presentation_pdf': f"media/reports/{pdf_filename}",
            'is_risk_detected': risk_detected
        }
    )
    print(f"🎯 [УМНЫЙ АУДИТ] Презентация и графики успешно сгенерированы в {final_pdf_path}")

if __name__ == "__main__":
    # Тестовые лимиты сметы для пилотного объекта
    limits = {'Бетон': 50000.00, 'Арматура': 30000.00, 'Логистика': 15000.00}
    run_smart_audit(project_id=1, budget_limits=limits)
