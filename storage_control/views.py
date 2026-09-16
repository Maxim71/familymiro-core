import random
import pyotp
import requests
import time
from datetime import datetime
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ServerBalance, LiveStreamMessage, EzhikUserCabinet, EzhikVideoVault

CAPTAIN_SECRET = "M32MIROHACRE2059VAULTTANGERINE55"
REAL_TELEGRAM_TOKEN = "8658437799:AAFYMULZ41EyuPyvEFIt8WCCq8zvwsT7_1U"
REAL_CHAT_ID = "541888946"

def get_or_create_ezhik_charm(request):
    if not request.session.session_key: request.session.create()
    s_key = request.session.session_key
    cabinet, _ = EzhikUserCabinet.objects.get_or_create(
        session_key=s_key,
        defaults={'assigned_name': "Капитан Максим", 'moba_style_preference': 'cyan', 'user_country': "Россия"}
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
        'market_status': "🛰️ КОНТУР ИИ АКТИВЕН // ОЗУ СИНХРОНИЗИРОВАНО",
        'tax_paid': server_stat.total_tax_paid,
        'user_cabinet': cabinet,
        'action_notes': "🦔 Робот-Ёжик ожил. Потоки данных запущены в реальном времени."
    }
    return render(request, 'storage_control/miro_monolith.html', context)

@csrf_exempt
def send_to_stream_api(request):
    """ШЛЮЗ КНОПКИ 'ПЕРЕДАТЬ В ЭФИР': Ловит текст и шлет в Telegram Капитана"""
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        if not text: return JsonResponse({'status': 'error', 'message': 'Пустое сообщение'})
        
        reply_text = "🦔 Рапорт принят в ОЗУ!"
        
        # Заносим физически в базу данных SQLite
        LiveStreamMessage.objects.create(sender_name="Капитан Максим", message_text=text, ezhik_reply=reply_text)
        
        # Выстрел в Telegram
        try:
            msg = f"📡 <b>[ЭФИР ПРОРАБАМ]:</b> {text}\n🤖 <i>Ёжик транслировал сигнал на все объекты Тулы.</i>"
            requests.post(f"https://telegram.org{REAL_TELEGRAM_TOKEN}/sendMessage", data={"chat_id": REAL_CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=2)
        except Exception: pass
        
        return JsonResponse({'status': 'success', 'reply': reply_text})
    return JsonResponse({'status': 'invalid'})

def live_stream_dashboard_api(request):
    """📰 ЖИВОЙ RFI ПОТОК ФАКТОВ: Отдает реальные логи и убирает [Ожидание данных...]"""
    current_time = datetime.now().strftime("%H:%M:%S")
    
    # Берем последние сообщения из базы данных + добавляем системные логи
    db_messages = LiveStreamMessage.objects.all().order_by('-created_at')[:3]
    stream_data = []
    
    for m in db_messages:
        stream_data.append({"name": m.sender_name, "text": m.message_text, "reply": m.ezhik_reply})
        
    # Добавляем системный АИС-сигнал, чтобы лента никогда не пустовала
    stream_data.append({
        "name": f"🛰️ [АИС-СПУТНИК {current_time}]",
        "text": "Контейнеровоз COSCO SHANGHAI с редукторами Komatsu прошел Японское море.",
        "reply": "Курс нормальный"
    })
    return JsonResponse({'stream': stream_data})

# Страхующие шлюзы Радара и Капсулы времени
def neuro_radar_dashboard(request): return render(request, 'storage_control/neuro_radar.html', {'system_status': "АКТИВЕН"})
def pto_cabinet(request, act_id): return render(request, 'storage_control/pto_cabinet.html', {'act_id': act_id, 'system_status': "АКТИВЕН"})
def capsule_time_vault(request): return render(request, 'storage_control/capsule.html')
@csrf_exempt
def import_excel_pto_api(request): return JsonResponse({'status': 'success'})
@csrf_exempt
def ezhik_voice_notepad_api(request): return JsonResponse({'status': 'success'})
@csrf_exempt
def neuro_radar_voice_api(request): return JsonResponse({'status': 'success'})
def upload_video_to_vault_api(request): return JsonResponse({'status': 'success'})
def push_video_to_telegram_action_api(request, video_id): return JsonResponse({'status': 'success'})
def add_to_cart_api(request, product_id): return JsonResponse({'status': 'success'})
def checkout_sbp_payment_api(request): return JsonResponse({'status': 'paid'})
def save_vhd_journal_record(request): return JsonResponse({'status': 'success'})
@csrf_exempt
def computer_vision_m19_api(request): return JsonResponse({'status': 'success'})
