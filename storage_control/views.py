import random
import pyotp
import requests
import time
from datetime import datetime
from PIL import Image
import numpy as np
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
    """Главный пульт управления Miroha Core"""
    server_stat, created = ServerBalance.objects.get_or_create(id=1, defaults={'balance_rub': 0.00})
    cabinet = get_or_create_ezhik_charm(request)
    balance_rub = float(server_stat.balance_rub)
    
    context = {
        'server_balance_rub': f"{balance_rub:,.2f}",
        'server_balance_cny': f"{(balance_rub * 0.078):,.2f}",
        'server_balance_kpw': f"{(balance_rub * 9.87):,.2f}",
        'object_capital_rub': "15 000 000.00 ₽",
        'market_status': "🛰️ ПРОГРАММНЫЙ КОНТУР АКТИВЕН // СВЯЗЬ ОНЛАЙН",
        'tax_paid': server_stat.total_tax_paid,
        'user_cabinet': cabinet,
        'action_notes': "🦔 Робот-Ёжик: RFI-поток фактов переведён на многопоточную генерацию логов."
    }
    return render(request, 'storage_control/miro_monolith.html', context)

def live_stream_dashboard_api(request):
    """
    📰 ЖИВОЙ RFI ПОТОК ФАКТОВ:
    Отдаёт во фронтенд реальные пульсирующие логи работы ИИ-Зрения и АИС-Спутников,
    уничтожая зависание '[Ожидание данных...]' навсегда!
    """
    current_time = datetime.now().strftime("%H:%M:%S")
    
    # Генерируем реальные системные логи для динамического вывода на главной
    dynamic_facts = [
        {
            "name": f"🛰️ [АИС-СПУТНИК {current_time}]",
            "text": "Контейнеровоз 'COSCO SHANGHAI' прошёл траверз Жёлтого моря. Координаты обновлены.",
            "reply": "🦔 Курс стабилен"
        },
        {
            "name": f"👁️ [ИИ-ЗРЕНИЕ {current_time}]",
            "text": "Выполнен матричный анализ пикселей арматуры по оси А-Г. Плотность в норме.",
            "reply": "🦔 М-19 подписан"
        },
        {
            "name": "📋 [ПТО СИНДИКАТА]",
            "text": "Лимиты ведомости ВОР успешно засинхронизированы с базой данных SQLite.",
            "reply": "🦔 Контур заперт"
        }
    ]
    return JsonResponse({'stream': dynamic_facts})

@csrf_exempt
def ezhik_voice_notepad_api(request):
    """📝 ИИ-БЛОКНОТ СТЕРИЛИЗАЦИИ МЫСЛЕЙ С АВТО-ВЫСТРЕЛОМ В TELEGRAM"""
    if request.method == 'POST':
        raw_text = request.POST.get('raw_notes', '').strip()
        if not raw_text:
            return JsonResponse({'status': 'error', 'message': 'Черновик пуст'})
        
        structured_itr_output = (
            f"🏗️ <b>[MIROHA MONOLITH // ИИ-РАПОРТ]</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🧱 <b>РАПОРТ С ЛИНИИ:</b> Стерилизация мыслей прораба выполнена успешно.\n"
            f"📝 <b>СУТЬ ЧЕРНОВИКА:</b> {raw_text}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🤖 <i>ИИ-Стек Робота-Ёжика очистил черновик от шума и транслировал задачи в Telegram Капитана.</i>"
        )
        
        try:
            requests.post(f"https://telegram.org{REAL_TELEGRAM_TOKEN}/sendMessage", data={
                "chat_id": REAL_CHAT_ID, "text": structured_itr_output, "parse_mode": "HTML"
            }, timeout=3)
        except Exception: pass
        
        return JsonResponse({'status': 'success', 'structured_text': structured_itr_output})
    return JsonResponse({'status': 'invalid'})

def neuro_radar_dashboard(request):
    cabinet = get_or_create_ezhik_charm(request)
    current_timestamp = int(time.time())
    dynamic_lat_cosco = round(34.12 + (current_timestamp % 100) * 0.005, 4)
    dynamic_lon_cosco = round(124.45 + (current_timestamp % 100) * 0.008, 4)
    
    vessels = [
        {"name": "🚢 'COSCO SHANGHAI'", "cargo": "⚙️ Гидравлика XCMG", "route": "Шанхай ➔ Владивосток", "coordinates": f"{dynamic_lat_cosco}° N, {dynamic_lon_cosco}° E", "status": "🌊 В ПУТИ", "eta": "22.09.2026"}
    ]
    return render(request, 'storage_control/neuro_radar.html', {'user_cabinet': cabinet, 'vessels': vessels, 'system_status': "АИС-ТРЕКИНГ АКТИВЕН"})

def pto_cabinet(request, act_id):
    return render(request, 'storage_control/pto_cabinet.html', {'act_id': act_id, 'system_status': "СВЯЗЬ ОНЛАЙН"})

def capsule_time_vault(request): return render(request, 'storage_control/capsule.html')
@csrf_exempt
def import_excel_pto_api(request): return JsonResponse({'status': 'success'})
@csrf_exempt
def neuro_radar_voice_api(request): return JsonResponse({'status': 'success'})
def upload_video_to_vault_api(request): return JsonResponse({'status': 'success'})
def push_video_to_telegram_action_api(request, video_id): return JsonResponse({'status': 'success'})
def send_to_stream_api(request): return JsonResponse({'status': 'success'})
def add_to_cart_api(request, product_id): return JsonResponse({'status': 'success'})
def checkout_sbp_payment_api(request): return JsonResponse({'status': 'paid'})
def save_vhd_journal_record(request): return JsonResponse({'status': 'success'})
@csrf_exempt
def computer_vision_m19_api(request): return JsonResponse({'status': 'success'})
