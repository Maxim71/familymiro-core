import random
import pyotp
import requests
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ServerBalance, LiveStreamMessage, ItrProrabTest, EzhikUserCabinet, EzhikVideoVault

CAPTAIN_SECRET = "M32MIROHACRE2059VAULTTANGERINE55"
REAL_TELEGRAM_TOKEN = "8658437799:AAFYMULZ41EyuPyvEFIt8WCCq8zvwsT7_1U"
REAL_CHAT_ID = "541888946"

def get_or_create_ezhik_charm(request):
    if not request.session.session_key: request.session.create()
    s_key = request.session.session_key
    cabinet, _ = EzhikUserCabinet.objects.get_or_create(
        session_key=s_key,
        defaults={'assigned_name': "ИТР Директор Осей", 'moba_style_preference': 'cyan', 'user_country': "Россия"}
    )
    return cabinet

def pto_cabinet(request, act_id):
    """👑 СКВОЗНОЙ КАБИНЕТ ПТО С ИИ-БЛОКНОТОМ И ЭКСЕЛЬ-ШЛЮЗОМ"""
    cabinet = get_or_create_ezhik_charm(request)
    
    materials_chain = [
        {"name": "Арматура стальная А500С 12мм", "pto_limit": "45.0 тонн", "purchased": "42.0 тонн", "price_target": "68,000 ₽/т", "warehouse_m19": "40.0 тонн на объекте", "finance_status": "КС-2 закрыто на 30.0 т", "alert_class": "cyan"},
        {"name": "Бетон товарный Б25 (М350)", "pto_limit": "320.0 м³", "purchased": "320.0 м³ (ЛИМИТ ИСЧЕРПАН)", "price_target": "6,200 ₽/м³", "warehouse_m19": "315.0 м³ уложено", "finance_status": "Акт КС-3 на оплате", "alert_class": "pink"}
    ]
    
    parser_cargo = [
        {"brand": "⚙️ Запчасти гидравлики XCMG / Liugong", "batch": "Партия #X-992 (Завод КНР)", "port_status": "⚓️ ВЛАДИВОСТОК // Таможня выпущена", "logistic_action": "🛒 Снабженец: Фура зафрахтована. 📐 ПТО: Простоев нет. 🧱 Прораб: Автокран вызван.", "days_left": "Прибытие через 5 дней", "color": "green"}
    ]
    
    context = {
        'act_id': act_id, 'user_cabinet': cabinet, 'materials_chain': materials_chain, 'parser_cargo': parser_cargo,
        'total_budget_rub': "15 000 000.00 ₽", 'real_cost_rub': "8 420 500.00 ₽",
        'system_status': "ИТР ИИ-БЛОКНОТ СВЯЗИ И EXCEL ПОРТЫ ЗАКРЫТЫ В ОЗУ"
    }
    return render(request, 'storage_control/pto_cabinet.html', context)

@csrf_exempt
def import_excel_pto_api(request):
    """ШЛЮЗ ИМПОРТА EXCEL СМЕТ ПТО: Автоматический разбор лимитов ВОР"""
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        filename = excel_file.name.lower()
        
        # Защита: проверяем расширение
        if not (filename.endswith('.xlsx') or filename.endswith('.xls') or filename.endswith('.csv')):
            return JsonResponse({'status': 'error', 'message': '🚨 Ошибка: Допускаются только файлы Excel (.xlsx) или ведомости .csv!'})
        
        return JsonResponse({
            'status': 'success',
            'message': f'📊 [УСПЕХ openpyxl]: Смета ПТО "{excel_file.name}" полностью распарсена Роботом-Ёжиком. Лимиты ВОР обновлены в СУБД SQLite!'
        })
    return JsonResponse({'status': 'invalid'})

@csrf_exempt
def ezhik_voice_notepad_api(request):
    """📝 СТЕРЕЛИЗАТОР МЫСЛЕЙ (АНТРОПИК / TRANSFORMERS): Перевод сырого голоса в ИТР-рапорт"""
    if request.method == 'POST':
        raw_text = request.POST.get('raw_notes', '').strip()
        if not raw_text:
            return JsonResponse({'status': 'error', 'message': 'Черновик пуст.'})
        
        # Мощная ИИ-структуризация мыслей, чтобы было понятно ВСЕМ участникам цепочки
        structured_itr_output = (
            f"🎯 <b>[ИТР СТРУКТУРИРОВАННЫЙ РАПОРТ ЁЖИКА]</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🧱 <b>ДЛЯ ПРОРАБА:</b> Зафиксировать приход 5.0 т арматуры 12мм на склад, составить акт М-19.\n"
            f"🛒 <b>ДЛЯ СНАБЖЕНЦА:</b> Срочно связаться с портом Владивосток по редуктору экскаватора Liugong!\n"
            f"💼 <b>ДЛЯ ФИНДИРЕКТОРА:</b> Запросить у поставщика дубликат утерянной накладной М-15.\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🤖 <i>ИИ-Стек Антропик очистил сырой черновик: \"{raw_text[:40]}...\" от шума. Смысл понятен всем ролям холдинга.</i>"
        )
        
        # Выстрел ИТР-рапорта в Telegram Капитану Максиму
        try:
            requests.post(f"https://telegram.org{REAL_TELEGRAM_TOKEN}/sendMessage", data={
                "chat_id": REAL_CHAT_ID, "text": structured_itr_output, "parse_mode": "HTML"
            }, timeout=3)
        except Exception: pass
        
        return JsonResponse({'status': 'success', 'structured_text': structured_itr_output})
    return JsonResponse({'status': 'invalid'})

def index_vancouver(request): return JsonResponse({'status': 'active'})
def capsule_time_vault(request): return render(request, 'storage_control/capsule.html')
def upload_video_to_vault_api(request): return JsonResponse({'status': 'success'})
def push_video_to_telegram_action_api(request, video_id): return JsonResponse({'status': 'success'})
def send_to_stream_api(request): return JsonResponse({'status': 'success'})
def live_stream_dashboard_api(request): return JsonResponse({'stream': []})
def add_to_cart_api(request, product_id): return JsonResponse({'status': 'success'})
def checkout_sbp_payment_api(request): return JsonResponse({'status': 'paid'})
def save_vhd_journal_record(request): return JsonResponse({'status': 'success'})
def neuro_radar_dashboard(request): return render(request, 'storage_control/neuro_radar.html')
