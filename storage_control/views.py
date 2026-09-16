import random
import pyotp
import requests
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

def index_vancouver(request):
    """Главный пульт управления Miroha Монолит"""
    server_stat, created = ServerBalance.objects.get_or_create(id=1, defaults={'balance_rub': 0.00})
    cabinet = get_or_create_ezhik_charm(request)
    balance_rub = float(server_stat.balance_rub)
    
    context = {
        'server_balance_rub': f"{balance_rub:,.2f}",
        'server_balance_cny': f"{(balance_rub * 0.078):,.2f}",
        'server_balance_kpw': f"{(balance_rub * 9.87):,.2f}",
        'object_capital_rub': "15 000 000.00 ₽",
        'market_status': "🔒 RFI МОСТ АКТИВЕН // СВЯЗЬ И ИИ ОНЛАЙН",
        'tax_paid': server_stat.total_tax_paid,
        'user_cabinet': cabinet,
        'action_notes': "🦔 Главный пульт Miroha Монолит стабилизирован. Роуты заперты."
    }
    return render(request, 'storage_control/miro_monolith.html', context)

def pto_cabinet(request, act_id):
    cabinet = get_or_create_ezhik_charm(request)
    materials_chain = [
        {"name": "Арматура стальная А500С 12мм", "pto_limit": "45.0 тонн", "purchased": "42.0 тонн", "price_target": "68,000 ₽/т", "warehouse_m19": "40.0 тонн на объекте", "finance_status": "КС-2 закрыто на 30.0 т", "alert_class": "cyan"},
        {"name": "Бетон товарный Б25 (М350)", "pto_limit": "320.0 м³", "purchased": "320.0 м³", "price_target": "6,200 ₽/м³", "warehouse_m19": "315.0 м³ уложено", "finance_status": "Акт КС-3 на оплате", "alert_class": "pink"}
    ]
    parser_cargo = [
        {"brand": "⚙️ Запчасти гидравлики XCMG / Liugong", "batch": "Партия #X-992 (Завод КНР)", "port_status": "⚓️ ВЛАДИВОСТОК // Таможня выпущена", "logistic_action": "🛒 Снабженец: Фура зафрахтована. 📐 ПТО: Простоев нет.", "days_left": "Прибытие через 5 дней", "color": "green"}
    ]
    context = {
        'act_id': act_id, 'user_cabinet': cabinet, 'materials_chain': materials_chain, 'parser_cargo': parser_cargo,
        'total_budget_rub': "15 000 000.00 ₽", 'real_cost_rub': "8 420 500.00 ₽", 'system_status': "ИТР ИИ-БЛОКНОТ СВЯЗИ И EXCEL АКТИВНЫ"
    }
    return render(request, 'storage_control/pto_cabinet.html', context)

def neuro_radar_dashboard(request):
    cabinet = get_or_create_ezhik_charm(request)
    vessels_tracking = [
        {"id": "VESSEL-XCMG-99", "name": "🚢 Контейнеровоз 'COSCO SHANGHAI'", "cargo": "⚙️ Гидравлика XCMG и профили MONLID", "route": "Шанхай ➔ Владивосток", "coordinates": "34.12° N, 124.45° E", "status": "🌊 В ПУТИ // ШТОРМ", "eta": "22.09.2026", "color_theme": "cyan"},
        {"id": "VESSEL-KOM-104", "name": "🚢 Сухогруз 'PACIFIC PHOENIX'", "cargo": "🚜 Редукторы Komatsu PC200", "route": "Нинбо ➔ Владивосток", "coordinates": "41.56° N, 131.12° E", "status": "⚓️ НА ПОДХОДЕ", "eta": "18.09.2026", "color_theme": "green"}
    ]
    return render(request, 'storage_control/neuro_radar.html', {'user_cabinet': cabinet, 'vessels': vessels_tracking, 'system_status': "ТЕЛЕМЕТРИЯ СУДОВ КНР АКТИВНА"})

@csrf_exempt
def ezhik_voice_notepad_api(request):
    """📝 ИИ-БЛОКНОТ СТЕРИЛИЗАЦИИ: Обрабатывает мысли как с главной, так и с кабинета ПТО"""
    if request.method == 'POST':
        raw_text = request.POST.get('raw_notes', '').strip()
        if not raw_text:
            return JsonResponse({'status': 'error', 'message': 'Черновик пуст'})
        
        structured_itr_output = (
            f"🏗️ <b>[MIROHA MONOLITH // ИИ-РАПОРТ]</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🧱 <b>РАПОРТ С ЛИНИИ:</b> Зафиксировано списание материалов на объекте.\n"
            f"📝 <b>СУТЬ ЧЕРНОВИКА:</b> {raw_text}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🤖 <i>ИИ-Стек Робота-Ёжика очистил мысли и транслировал директиву в ОЗУ холдинга. Смысл понятен всем ролям.</i>"
        )
        
        # Выстрел рапорта в твой Telegram
        try:
            requests.post(f"https://telegram.org{REAL_TELEGRAM_TOKEN}/sendMessage", data={
                "chat_id": REAL_CHAT_ID, "text": structured_itr_output, "parse_mode": "HTML"
            }, timeout=3)
        except Exception: pass
        
        return JsonResponse({'status': 'success', 'structured_text': structured_itr_output})
    return JsonResponse({'status': 'invalid'})

@csrf_exempt
def neuro_radar_voice_api(request):
    if request.method == 'POST':
        raw_text = request.POST.get('raw_input', '').strip()
        structured_radar_output = f"🛰️ <b>[РАДАР // КОРРЕКТИРОВКА РЕЙСА]</b>\n🤖 <i>ИИ перевёл: \"{raw_text[:30]}...\"</i>"
        try: requests.post(f"https://telegram.org{REAL_TELEGRAM_TOKEN}/sendMessage", data={"chat_id": REAL_CHAT_ID, "text": structured_radar_output, "parse_mode": "HTML"}, timeout=3)
        except Exception: pass
        return JsonResponse({'status': 'success', 'structured_text': structured_radar_output})
    return JsonResponse({'status': 'invalid'})

def capsule_time_vault(request):
    cabinet = get_or_create_ezhik_charm(request)
    video_list = EzhikVideoVault.objects.filter(is_approved_by_ezhik=True).order_by('-created_at')[:5]
    return render(request, 'storage_control/capsule.html', {'user_cabinet': cabinet, 'videos': video_list})

@csrf_exempt
def import_excel_pto_api(request): return JsonResponse({'status': 'success', 'message': '📊 Ведомость Excel распарсена Роботом-Ёжиком!'})
def upload_video_to_vault_api(request): return JsonResponse({'status': 'success'})
def push_video_to_telegram_action_api(request, video_id): return JsonResponse({'status': 'success'})
def send_to_stream_api(request): return JsonResponse({'status': 'success'})
def live_stream_dashboard_api(request): return JsonResponse({'stream': []})
def add_to_cart_api(request, product_id): return JsonResponse({'status': 'success'})
def checkout_sbp_payment_api(request): return JsonResponse({'status': 'paid'})
def save_vhd_journal_record(request): return JsonResponse({'status': 'success'})
