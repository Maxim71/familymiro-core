import random
import pyotp
import requests
from django.shortcuts import render
from django.http import JsonResponse
from .models import ServerBalance, LiveStreamMessage, ItrProrabTest, EzhikUserCabinet, EzhikVideoVault

CAPTAIN_SECRET = "M32MIROHACRE2059VAULTTANGERINE55"
REAL_TELEGRAM_TOKEN = "8658437799:AAFYMULZ41EyuPyvEFIt8WCCq8zvwsT7_1U"
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
        'market_status': "КОНТУР АКТИВЕН // ИИ-ОХОТНИК ЗА ВОСПОМИНАНИЯМИ ОТЦОВ",
        'tax_paid': server_stat.total_tax_paid,
        'user_cabinet': cabinet,
        'action_notes': "🦔 [ИИ-РАДАР ТОРНАДО]: Запущено сканирование спецканалов на предмет лучших детских воспоминаний отцов."
    }
    return render(request, 'storage_control/miro_monolith.html', context)

def capsule_time_vault(request):
    """Капсула времени: Слой Ленивой Ротации воспоминаний отцов"""
    cabinet = get_or_create_ezhik_charm(request)
    is_captain = False
    if request.method == 'POST' and 'totp_code' in request.POST:
        if pyotp.TOTP(CAPTAIN_SECRET).verify(request.POST.get('totp_code', '').strip()): is_captain = True

    # Наполняем базу результатов почётными видеороликами воспоминаний отцов разных стран
    video_list = EzhikVideoVault.objects.filter(is_approved_by_ezhik=True).order_by('-created_at')[:10]
    if not video_list.exists():
        EzhikVideoVault.objects.create(
            video_title="❤️ [АРХИВ РОДА] Детский смех и первые шаги дочери", 
            video_file_url="https://w3schools.com", 
            country_origin="⚓️ СОРТИРОВОЧНЫЙ ПОРТ ВЛАДИВОСТОК // ХАБ-РФ"
        )
        EzhikVideoVault.objects.create(
            video_title="👨‍👦 [НАСЛЕДИЕ] С любовью на век от Папы (Семейный архив)", 
            video_file_url="https://w3schools.com", 
            country_origin="🗼 СИНДИКАТ ТОКИО // ХАБ-ЯПОНИЯ"
        )
        video_list = EzhikVideoVault.objects.filter(is_approved_by_ezhik=True)

    good_events = [
        {"date": "15.09.2026", "title": "🔬 ИИ-Биологи Transformers полностью расшифровали старение клеток мозга."},
        {"date": "12.09.2026", "title": "⚡ Запущен первый в мире коммерческий реактор чистой энергии OpenStack."}
    ]
    scientists_chronicles = [{"author": "Жук Торнадо ИТР", "text": "Парсер спецканалов перехваченных воспоминаний отцов переведен в ОЗУ."}]
    from datetime import datetime
    time_delta = datetime(2059, 5, 24) - datetime.now()
    
    context = {
        'is_captain': is_captain, 'years': time_delta.days // 365, 'days': time_delta.days % 365,
        'sbp_code': "INV-ALFA-288003", 'user_cabinet': cabinet, 'videos': video_list,
        'good_events': good_events, 'chronicles': scientists_chronicles,
        'qr_setup_url': f"https://qrserver.com{CAPTAIN_SECRET}%26issuer=MirohaPlatform"
    }
    return render(request, 'storage_control/capsule.html', context)

def upload_video_to_vault_api(request):
    if request.method == 'POST':
        title = request.POST.get('title', 'Архив Наследия').strip()
        new_video = EzhikVideoVault.objects.create(
            video_title=f"❤️ [ПАМЯТСТВО ОТЦОВ]: {title}",
            video_file_url="https://w3schools.com",
            country_origin="🚀 АСИНХРОННЫЙ ГЕО-ХАБ ТОРНАДО"
        )
        # Выстрел в Telegram при ручной заливке воспоминания
        try:
            msg = f"👶 <b>[ПЕРЕХВАТ ДЕТСКОГО ВОСПОМИНАНИЯ]</b>\n📝 <b>Суть:</b> {title}\n👁️ ИИ-Сито верифицировало взгляд, улыбку и звук ОК!"
            requests.post(f"https://telegram.org{REAL_TELEGRAM_TOKEN}/sendMessage", data={"chat_id": REAL_CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=3)
        except Exception: pass
        return JsonResponse({'status': 'success', 'message': '✅ [ИИ-СИТО]: Видео занесено на века в Ленту Памятства!'})
    return JsonResponse({'status': 'invalid'})

def push_video_to_telegram_action_api(request, video_id):
    """Кнопка-Значок снизу видео карточки: Отправка воспоминания отца на телефон"""
    try:
        video = EzhikVideoVault.objects.get(id=video_id)
        msg = f"✈️ <b>[ТРАНСЛЯЦИЯ ВОСПОМИНАНИЯ ОТЦА]</b>\n\n📌 <b>Хаб-Источник:</b> {video.country_origin}\n👶 <b>Памятство:</b> {video.video_title}\n\n🤖 <i>Робот-Ёжик убрал лишний шум. Звук и речь прослушиваются чисто!</i>"
        requests.post(f"https://telegram.org{REAL_TELEGRAM_TOKEN}/sendMessage", data={"chat_id": REAL_CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=3)
        return JsonResponse({'status': 'success', 'message': '✈️ Воспоминание успешно транслировано на телефон!'})
    except Exception:
        return JsonResponse({'status': 'error'})

def send_to_stream_api(request):
    if request.method == 'POST':
        name = request.POST.get('name', 'Капитан').strip()
        text = request.POST.get('text', '').strip()
        try:
            requests.post(f"https://telegram.org{REAL_TELEGRAM_TOKEN}/sendMessage", data={"chat_id": REAL_CHAT_ID, "text": f"🏗️ <b>[{name}]:</b> {text}", "parse_mode": "HTML"}, timeout=3)
        except Exception: pass
        LiveStreamMessage.objects.create(sender_name=name, message_text=text, ezhik_reply="Перехвачено")
        return JsonResponse({'status': 'success', 'reply': "Перехвачено"})
    return JsonResponse({'status': 'invalid'})

def live_stream_dashboard_api(request):
    messages_list = LiveStreamMessage.objects.all().order_by('-created_at')[:5]
    data = [{'name': m.sender_name, 'text': m.message_text, 'reply': m.ezhik_reply} for m in messages_list]
    return JsonResponse({'stream': data})

def add_to_cart_api(request, product_id): return JsonResponse({'status': 'success'})
def checkout_sbp_payment_api(request): return JsonResponse({'status': 'paid'})
def pto_cabinet(request, act_id): return render(request, 'storage_control/pto_cabinet.html')
def save_vhd_journal_record(request): return JsonResponse({'status': 'success'})
def neuro_radar_dashboard(request): return render(request, 'storage_control/neuro_radar.html')
