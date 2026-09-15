import random
import pyotp
from django.shortcuts import render
from django.http import JsonResponse
from .models import ServerBalance, LiveStreamMessage, ItrProrabTest, EzhikUserCabinet, EzhikVideoVault

CAPTAIN_SECRET = "M32MIROHACRE2059VAULTTANGERINE55"

def get_or_create_ezhik_charm(request):
    if not request.session.session_key:
        request.session.create()
    s_key = request.session.session_key
    moba_names = ["Мастер Осей", "Вековой Хроникер", "Инфлюенсер Наследия", "RFI Диспетчер", "Продюсер Эфира"]
    moba_styles = ["cyan", "pink", "green", "gold"]
    cabinet, created = EzhikUserCabinet.objects.get_or_create(
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
        'market_status': "КОНТУР АКТИВЕН // PROTOCOL GIT-GATE-РТО",
        'tax_paid': server_stat.total_tax_paid,
        'user_cabinet': cabinet,
        'action_notes': f"🦔 [ШАРМ ЁЖИКА]: Гео-парсер Торнадо запущен. Видео-шлюзы портов Токио-Шанхай-Россия активны."
    }
    return render(request, 'storage_control/miro_monolith.html', context)

def capsule_time_vault(request):
    cabinet = get_or_create_ezhik_charm(request)
    is_captain = False
    error_msg = None
    
    if request.method == 'POST' and 'totp_code' in request.POST:
        code = request.POST.get('totp_code', '').strip()
        totp = pyotp.TOTP(CAPTAIN_SECRET)
        if totp.verify(code): is_captain = True
        else: error_msg = "🚨 КРИПТО-ОШИБКА: Неверный TOTP код!"

    # 🎬 ЖУК ТОРНАДО ПАРСИТ И НАПОЛНЯЕТ БАЗУ ГЕО-МЕТКАМИ ПОРТОВ И ХАБОВ
    video_list = EzhikVideoVault.objects.filter(is_approved_by_ezhik=True)
    if not video_list.exists():
        EzhikVideoVault.objects.create(
            video_title="Детский смех и первые шаги по осям ИТР", 
            video_file_url="https://w3schools.com", 
            country_origin="⚓️ СОРТИРОВОЧНЫЙ ПОРТ ВЛАДИВОСТОК // ХАБ-РФ"
        )
        EzhikVideoVault.objects.create(
            video_title="Промышленный запуск конвейера MONLID", 
            video_file_url="https://w3schools.com", 
            country_origin="🏭 ПРОМЫШЛЕННЫЙ КОНТУР ШАНХАЙ // ХАБ-КНР"
        )
        EzhikVideoVault.objects.create(
            video_title="Семейный архив людей Вечности Токио", 
            video_file_url="https://w3schools.com", 
            country_origin="🗼 СИНДИКАТ ТОКИО-ЧЕРНЬ // ХАБ-ЯПОНИЯ"
        )
        EzhikVideoVault.objects.create(
            video_title="Мультимодальный рейс снабжения VAN-992", 
            video_file_url="https://w3schools.com", 
            country_origin="🌊 ТРАНЗИТНЫЙ ПОРТ ВАНКУВЕР // ХАБ-КАНАДА"
        )
        video_list = EzhikVideoVault.objects.filter(is_approved_by_ezhik=True)

    good_events = [
        {"date": "15.09.2026", "title": "🔬 ИИ-Биологи полностью расшифровали механизмы старения клеток мозга."},
        {"date": "12.09.2026", "title": "⚡ Запущен первый в мире коммерческий реактор чистой энергии."}
    ]
    
    scientists_chronicles = [
        {"author": "Академик ИТР Синдиката", "text": "Мы закладываем этот программный код в ОЗУ Tangerine Natrium как памятник того, что в 2026 году человек научился передавать волю через ИИ-контуры."}
    ]

    from datetime import datetime
    target_date = datetime(2059, 5, 24, 0, 0, 0)
    time_delta = target_date - datetime.now()
    
    context = {
        'is_captain': is_captain, 'error_msg': error_msg,
        'years': time_delta.days // 365, 'days': time_delta.days % 365,
        'sbp_code': "INV-ALFA-288003", 'user_cabinet': cabinet, 'videos': video_list,
        'good_events': good_events, 'chronicles': scientists_chronicles,
        'qr_setup_url': f"https://qrserver.com{CAPTAIN_SECRET}%26issuer=MirohaPlatform"
    }
    return render(request, 'storage_control/capsule.html', context)

def upload_video_to_vault_api(request):
    if request.method == 'POST':
        title = request.POST.get('title', 'Архив').strip()
        port_choice = random.choice([
            "⚓️ СОРТИРОВОЧНЫЙ ПОРТ ВЛАДИВОСТОК", 
            "🏭 ПРОМЫШЛЕННЫЙ КОНТУР ШАНХАЙ", 
            "🗼 СИНДИКАТ ТОКИО-ЧЕРНЬ", 
            "🌊 ТРАНЗИТНЫЙ ПОРТ ВАНКУВЕР"
        ])
        EzhikVideoVault.objects.create(
            video_title=title,
            video_file_url="https://w3schools.com",
            country_origin=f"📡 ЖУК ПАРСЕР: {port_choice} // СЛОЙ_0"
        )
        return JsonResponse({'status': 'success', 'message': '✅ Видео успешно пробилось через сито и гео-парсер!'})
    return JsonResponse({'status': 'invalid'})

def send_to_stream_api(request): return JsonResponse({'status': 'success'})
def live_stream_dashboard_api(request): return JsonResponse({'stream': []})
def add_to_cart_api(request, product_id): return JsonResponse({'status': 'success'})
def checkout_sbp_payment_api(request): return JsonResponse({'status': 'paid'})
def pto_cabinet(request, act_id): return render(request, 'storage_control/pto_cabinet.html')
def save_vhd_journal_record(request): return JsonResponse({'status': 'success'})
def neuro_radar_dashboard(request): return render(request, 'storage_control/neuro_radar.html')
