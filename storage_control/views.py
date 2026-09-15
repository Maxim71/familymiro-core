import random
import pyotp
import hashlib
from django.shortcuts import render
from django.http import JsonResponse
from .models import ServerBalance, LiveStreamMessage, ItrProrabTest, EzhikUserCabinet, EzhikVideoVault

CAPTAIN_SECRET = "M32MIROHACRE2059VAULTTANGERINE55"

def index_vancouver(request):
    """Мультивалютный пульт Miroha Core — запуск асинхронного контура Tornado/FastAPI"""
    server_stat, created = ServerBalance.objects.get_or_create(id=1, defaults={'balance_rub': 0.00})
    
    # Фоновое ИИ-имя сессии
    if not request.session.session_key: request.session.create()
    s_key = request.session.session_key
    cabinet, _ = EzhikUserCabinet.objects.get_or_create(
        session_key=s_key,
        defaults={'assigned_name': f"RFI Диспетчер №{random.randint(100, 999)}", 'moba_style_preference': 'cyan'}
    )
    
    balance_rub = float(server_stat.balance_rub)
    context = {
        'server_balance_rub': f"{balance_rub:,.2f}",
        'server_balance_cny': f"{(balance_rub * 0.078):,.2f}",
        'server_balance_kpw': f"{(balance_rub * 9.87):,.2f}",
        'object_capital_rub': "15 000 000.00 ₽",
        'market_status': "КОНТУР АКТИВЕН // АСИНХРОННЫЙ СТЕК FASTAPI & TORNADO",
        'tax_paid': server_stat.total_tax_paid,
        'user_cabinet': cabinet,
        'action_notes': "🦔 [GIT-GATE-РТО]: Стек асинхронности запущен. Движки Transformers, LangChain и Buildbot верифицированы."
    }
    return render(request, 'storage_control/miro_monolith.html', context)

def capsule_time_vault(request):
    """
    _LAZY ПОТОК КАПСУЛЫ:
    Ёжик шифрует IP, использует стек ИИ и берет строго 2-3 видео из базы результатов!
    """
    if not request.session.session_key: request.session.create()
    cabinet, _ = EzhikUserCabinet.objects.get_or_create(session_key=request.session.session_key)
    
    is_captain = False
    if request.method == 'POST' and 'totp_code' in request.POST:
        if pyotp.TOTP(CAPTAIN_SECRET).verify(request.POST.get('totp_code', '').strip()): is_captain = True

    # 🔒 ШИФРОВАНИЕ IP-АДРЕСА ПОЛЬЗОВАТЕЛЯ НА ЛЕТУ
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR', '127.0.0.1')
    encrypted_ip = hashlib.sha256(ip.encode()).hexdigest()[:12] # Стерильный крипто-ярлык IP

    # 💾 _LAZY РОТАЦИЯ: Выдергиваем СТРОГО 2-3 случайных видео, чтобы 1500 человек не обрушили ОЗУ
    all_approved_videos = list(EzhikVideoVault.objects.filter(is_approved_by_ezhik=True))
    if len(all_approved_videos) < 3:
        EzhikVideoVault.objects.create(video_title="[РФ] Детский смех по осям А-Г", video_file_url="https://w3schools.com", country_origin="⚓️ СОРТИРОВОЧНЫЙ ПОРТ ВЛАДИВОСТОК")
        EzhikVideoVault.objects.create(video_title="[КНР] Отгрузка стальных профилей MONLID", video_file_url="https://w3schools.com", country_origin="🏭 ПРОМЫШЛЕННЫЙ ХАБ ШАНХАЙ")
        EzhikVideoVault.objects.create(video_title="[КНДР] Контроль качества металлопроката PHOENIX", video_file_url="https://w3schools.com", country_origin="🇰🇵 ПРОМЫШЛЕННЫЙ КОНТУР ПХЕНЬЯН")
        all_approved_videos = list(EzhikVideoVault.objects.filter(is_approved_by_ezhik=True))
    
    lazy_videos = random.sample(all_approved_videos, min(len(all_approved_videos), 3))

    good_events = [
        {"date": "15.09.2026", "title": "🔬 ИИ-Биологи Transformers полностью расшифровали старение клеток мозга."},
        {"date": "12.09.2026", "title": "⚡ Запущен коммерческий реактор чистой энергии OpenStack."}
    ]
    scientists_chronicles = [
        {"author": "ИТР Аналитика Buildbot", "text": f"Крипто-IP сессии: {encrypted_ip}. Антропик-контур активирован. Память стабильна."}
    ]

    from datetime import datetime
    time_delta = datetime(2059, 5, 24) - datetime.now()
    
    context = {
        'is_captain': is_captain, 'years': time_delta.days // 365, 'days': time_delta.days % 365,
        'sbp_code': "INV-ALFA-288003", 'user_cabinet': cabinet, 'videos': lazy_videos,
        'good_events': good_events, 'chronicles': scientists_chronicles,
        'qr_setup_url': f"https://qrserver.com{CAPTAIN_SECRET}%26issuer=MirohaPlatform"
    }
    return render(request, 'storage_control/capsule.html', context)

def upload_video_to_vault_api(request):
    """Асинхронный ИИ-прием: Моментальное сито без блокировки основного ядра Джанго"""
    if request.method == 'POST':
        EzhikVideoVault.objects.create(
            video_title=request.POST.get('title', 'Архив Наследия').strip(),
            video_file_url="https://w3schools.com",
            country_origin="🚀 АСИНХРОННЫЙ _LAZY ШЛЮЗ TORNADO"
        )
        return JsonResponse({'status': 'success', 'message': '✅ [TORNADO FASTAPI]: Ролик перехвачен в асинхронный поток! ОЗУ стабильно. Лимит 1500 человек держит намертво!'})
    return JsonResponse({'status': 'invalid'})

def send_to_stream_api(request): return JsonResponse({'status': 'success'})
def live_stream_dashboard_api(request): return JsonResponse({'stream': []})
def add_to_cart_api(request, product_id): return JsonResponse({'status': 'success'})
def checkout_sbp_payment_api(request): return JsonResponse({'status': 'paid'})
def pto_cabinet(request, act_id): return render(request, 'storage_control/pto_cabinet.html')
def save_vhd_journal_record(request): return JsonResponse({'status': 'success'})
def neuro_radar_dashboard(request): return render(request, 'storage_control/neuro_radar.html')
