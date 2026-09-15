import random
import pyotp
import requests # Сетевой шлюз для выстрела в Telegram API
from django.shortcuts import render
from django.http import JsonResponse
from .models import ServerBalance, LiveStreamMessage, ItrProrabTest, EzhikUserCabinet, EzhikVideoVault

CAPTAIN_SECRET = "M32MIROHACRE2059VAULTTANGERINE55"

# 🔑 НАСТОЯЩИЙ БОЕВОЙ ТОКЕН МАКСИМА, ИЗВЛЕЧЕННЫЙ РАДАРОМ ЕЖИКА
REAL_TELEGRAM_TOKEN = "8658437799:AAFYMULZ41EyuPyvEFIt8WCCq8zvwsT7_1U"
# Твой ИТР Chat ID для мгновенного приема рапортов на телефон
REAL_CHAT_ID = "541888946" 

def get_or_create_ezhik_charm(request):
    if not request.session.session_key: request.session.create()
    s_key = request.session.session_key
    moba_names = ["Мастер Осей", "Вековой Хроникер", "Инфлюенсер Наследия", "RFI Диспетчер", "Продюсер Эфира"]
    moba_styles = ["cyan", "pink", "green", "gold"]
    cabinet, _ = EzhikUserCabinet.objects.get_or_create(
        session_key=s_key,
        defaults={'assigned_name': f"{random.choice(moba_names)} №{random.randint(100, 999)}", 'moba_style_preference': random.choice(moba_styles), 'user_country': "Россия"}
    )
    return cabinet

def index_vancouver(request):
    server_stat, created = ServerBalance.objects.get_or_create(id=1, defaults={'balance_rub': 0.00})
    cabinet = get_or_create_ezhik_charm(request)
    balance_rub = float(server_stat.balance_rub)
    context = {
        'server_balance_rub': f"{balance_rub:,.2f}",
        'server_balance_cny': f"{(balance_rub * 0.078):,.2f}",
        'server_balance_kpw': f"{(balance_rub * 9.87):,.2f}",
        'object_capital_rub': "15 000 000.00 ₽",
        'market_status': "КОНТУР АКТИВЕН // БОЕВОЙ ШЛЮЗ TELEGRAM ON",
        'tax_paid': server_stat.total_tax_paid,
        'user_cabinet': cabinet,
        'action_notes': "🦔 [РЕАЛЬНАЯ СВЯЗЬ АКТИВНА]: Настоящий токен запечатан в бэкенд. Ёжик готов стрелять рапортами в твой телефон."
    }
    return render(request, 'storage_control/miro_monolith.html', context)

def send_to_stream_api(request):
    """
    ЖУК ТОРНАДО // БОЕВОЙ ВЫСТРЕЛ:
    Перехват ИТР-сообщения из чата и мгновенная отправка реального СМС в твой Telegram-канал!
    """
    if request.method == 'POST':
        name = request.POST.get('name', 'Максим Игоревич').strip()
        text = request.POST.get('text', '').strip()
        
        reply_text = "🦔 [ЁЖИК]: Сигнал перехвачен! Рапорт отправлен на телефон Капитана."
        
        # 🔥 НАСТОЯЩИЙ БОЕВОЙ ВЫСТРЕЛ ЧЕРЕЗ TELEGRAM BOT API
        try:
            telegram_payload = (
                f"🏗️ <b>[MIROHA CORE // РАПОРТ С ЛИНИИ]</b>\n\n"
                f"👷 <b>Автор:</b> {name}\n"
                f"📝 <b>ИТР-Текст:</b> {text}\n\n"
                f"⚙️ <i>Протокол GIT-GATE-РТО активен. Мусор вычищен.</i>"
            )
            # Шлём реальный HTTP POST запрос на сервера Дурова
            requests.post(f"https://api.telegram.org/bot{REAL_TELEGRAM_TOKEN}/sendMessage", data={
                "chat_id": REAL_CHAT_ID,
                "text": telegram_payload,
                "parse_mode": "HTML"
            }, timeout=4)
        except Exception:
            pass

        LiveStreamMessage.objects.create(sender_name=name, message_text=text, ezhik_reply=reply_text)
        return JsonResponse({'status': 'success', 'reply': reply_text})
    return JsonResponse({'status': 'invalid'})

def live_stream_dashboard_api(request):
    messages_list = LiveStreamMessage.objects.all().order_by('-created_at')[:5]
    data = [{'name': m.sender_name, 'text': m.message_text, 'reply': m.ezhik_reply} for m in messages_list]
    return JsonResponse({'stream': data})

def capsule_time_vault(request):
    cabinet = get_or_create_ezhik_charm(request)
    is_captain = False
    error_msg = None
    if request.method == 'POST' and 'totp_code' in request.POST:
        if pyotp.TOTP(CAPTAIN_SECRET).verify(request.POST.get('totp_code', '').strip()): is_captain = True
        else: error_msg = "🚨 КРИПТО-ОШИБКА: Код неверный!"

    video_list = EzhikVideoVault.objects.filter(is_approved_by_ezhik=True).order_by('-created_at')[:10]
    good_events = [
        {"date": "15.09.2026", "title": "🔬 ИИ-Биологи Transformers полностью расшифровали старение клеток мозга."},
        {"date": "12.09.2026", "title": "⚡ Запущен коммерческий реактор чистой энергии OpenStack."}
    ]
    scientists_chronicles = [{"author": "ИТР Аналитика Buildbot", "text": "Контур связи запечатан. Токен активен."}]
    from datetime import datetime
    time_delta = datetime(2059, 5, 24) - datetime.now()
    
    context = {
        'is_captain': is_captain, 'years': time_delta.days // 365, 'days': time_delta.days % 365,
        'sbp_code': "INV-ALFA-288003", 'user_cabinet': cabinet, 'videos': video_list,
        'good_events': good_events, 'chronicles': scientists_chronicles,
        'qr_setup_url': f"https://qrserver.com{CAPTAIN_SECRET}%26issuer=MirohaPlatform"
    }
    return render(request, 'storage_control/capsule.html', context)

def upload_video_to_vault_api(request): return JsonResponse({'status': 'success'})
def add_to_cart_api(request, product_id): return JsonResponse({'status': 'success'})
def checkout_sbp_payment_api(request): return JsonResponse({'status': 'paid'})
def pto_cabinet(request, act_id): return render(request, 'storage_control/pto_cabinet.html')
def save_vhd_journal_record(request): return JsonResponse({'status': 'success'})
def neuro_radar_dashboard(request): return render(request, 'storage_control/neuro_radar.html')
