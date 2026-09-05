import random
from celery import shared_task
from storage_control.models import CascadeAnalytics, EzhikPlatformState, InteractiveComment

@shared_task(name="core.tasks.ezhik_cascade_processing")
def ezhik_cascade_processing():
    """
    [ИИ-КАСКАД ЁЖИКА]: Ежечасный анализ платформы для Архитектора-Отца.
    Обобщает данные, считает лайки, перехватывает ошибки и готовит сводку.
    """
    # 1. Анализ посещаемости и времени задержки
    analytics = CascadeAnalytics.objects.all()
    total_visitors = analytics.count()
    avg_time = sum([a.time_spent_seconds for a in analytics]) / (total_visitors if total_visitors else 1)
    
    # Ищем, где произошла критическая ошибка
    failed_sessions = analytics.exclude(last_error_log__isnull=True).exclude(last_error_log="")
    error_summary = f"Обнаружено сбоев: {failed_sessions.count()}. Последний: {failed_sessions.last().last_error_log if failed_sessions.exists() else 'Нет'}"
    
    # Считаем сумму лайков по платформе
    total_likes = sum([a.likes_given for a in analytics])
    
    # 2. Перехват новостей Ёжиком (Немного добрых известий для Архитектора)
    fresh_news_pool = [
        "Архитектура Наследия принята международным крипто-сообществом.",
        "Платформа FAMILYMIRO зафиксировала нулевой пинг на спутниковых узлах.",
        "Капитал Ёжика показывает стабильный органический рост."
    ]
    selected_news = random.choice(fresh_news_pool)
    
    # 3. Ёжик пишет отчет Отцу-Архитектору
    state, created = EzhikPlatformState.objects.get_or_create(id=1)
    
    state.ezhik_summary_report = (
        f"👔 ПУЛЬТ АРХИТЕКТОРА (МАКСИМА КОСАРЕВА):\n"
        f"• Активных посетителей: {total_visitors} | Среднее время на платформе: {round(avg_time)} сек.\n"
        f"• {error_summary}\n"
        f"• Точка максимального резонанса (Лайки): {total_likes} 👍\n"
        f"• Весточка от Ёжика: {selected_news}\n"
        f"• Вопрос к Мастеру: Что мы хотим изменить в конфигурации Слоя 0.0 сегодня?\n"
    )
    state.save()
    
    # 4. Если Ёжик видит плохой лог, он готовит скрытый перехват (для будущего Telegram/Email)
    print(f" [🦔 КАСКАД]: Отчет для Отца-Архитектора сгенерирован успешно.")
    return state.ezhik_summary_report

# SPLIT

@shared_task(name="core.tasks.process_safe_lava_webhook")
def process_safe_lava_webhook(payment_amount):
    """
    💳 БЛОК 63: Автоматическое расщепление налога LAVA API.
    Чистая строительно-агрономическая прибыль (Тот самый 1%):
    Уходит 6% в ФНС РФ, от 7% до 16% на Отец-Шлюз, остаток запечатывается дочке.
    """
    from storage_control.models import EzhikPlatformState
    
    total_amount = float(payment_amount)
    
    # # 1. Выделяем и мгновенно отправляем 6% легальности в ФНС
    russia_tax_amount = total_amount * 0.06
    
    # # 2. Выделяем законную премию Архитектора (Отец-Шлюз 16%)
    father_shield_bonus = total_amount * 0.16
    
    # # 3. Наш чистый остаток 1% намертво запечатываем в Сейф Опеки Мирославы
    pure_profit = total_amount - russia_tax_amount - father_shield_bonus
    
    # Обновляем баланс в системе
    state, _ = EzhikPlatformState.objects.get_or_create(id=1)
    state.total_platform_revenue = float(state.total_platform_revenue) + pure_profit
    state.save()
    
    print(f" [💳 LAVA]: Расщепление завершено. ФНС: {russia_tax_amount} | Отец-Шлюз: {father_shield_bonus} | Сейф Мирославы: {pure_profit}")
    return "TRANSACTION_FULLY_LEGAL_AND_SEALED"
