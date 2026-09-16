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
    cabinet, _ = EzhikUserCabinet.objects.get_or_create(
        session_key=s_key,
        defaults={'assigned_name': "ИТР Директор Осей", 'moba_style_preference': 'cyan', 'user_country': "Россия"}
    )
    return cabinet

def pto_cabinet(request, act_id):
    """
    👑 СВЯЗАННЫЙ ИТР-КАБИНЕТ + ЖУК ПАРСЕР (СЛОЙ_0):
    Автоматический трекинг ликвидного дефицита для Снабженца, ПТО и Прораба
    """
    cabinet = get_or_create_ezhik_charm(request)
    
    # Цепочка материалов внутри объекта
    materials_chain = [
        {
            "name": "Арматура стальная А500С 12мм",
            "pto_limit": "45.0 тонн",
            "purchased": "42.0 тонн",
            "price_target": "68,000 ₽/т",
            "warehouse_m19": "40.0 тонн на объекте",
            "finance_status": "КС-2 закрыто на 30.0 т",
            "alert_class": "cyan"
        },
        {
            "name": "Бетон товарный Б25 (М350)",
            "pto_limit": "320.0 м³",
            "purchased": "320.0 м³ (ЛИМИТ ИСЧЕРПАН)",
            "price_target": "6,200 ₽/м³",
            "warehouse_m19": "315.0 м³ уложено",
            "finance_status": "Акт КС-3 на оплате",
            "alert_class": "pink"
        }
    ]
    
    # 🔥 ЖУК ПАРСЕР // СЛОЙ_0: Ликвидный дефицит и запчасти спецтехники из портов
    parser_cargo_incoming = [
        {
            "brand": "⚙️ Запчасти гидравлики XCMG / Liugong",
            "batch": "Партия #X-992 (Завод КНР)",
            "port_status": "⚓️ ВЛАДИВОСТОК // Таможня выпущена",
            "logistic_action": "🛒 Снабженец: Фура зафрахтована. 📐 ПТО: Простоев нет. 🧱 Прораб: Автокран вызван к 21.09!",
            "days_left": "Прибытие через 5 дней",
            "color": "green"
        },
        {
            "brand": "🚜 Бортовые редукторы Komatsu PC200",
            "batch": "Партия #K-104 (Транзит Шанхай)",
            "port_status": "🏭 ПОРТ ШАНХАЙ // Погрузка на судно",
            "logistic_action": "🛒 Снабженец: Мониторинг карго. 📐 ПТО: Сдвиг графика на 3 дня.",
            "days_left": "В пути: 12 дней",
            "color": "pink"
        }
    ]
    
    context = {
        'act_id': act_id,
        'user_cabinet': cabinet,
        'materials_chain': materials_chain,
        'parser_cargo': parser_cargo_incoming,
        'total_budget_rub': "15 000 000.00 ₽",
        'real_cost_rub': "8 420 500.00 ₽",
        'profit_margin': "43.8%",
        'system_status': "ЖУК-ПАРСЕР СЛОЙ_0: АКТИВЕН // ИМПОРТ СПЕЦТЕХНИКИ ПОДКЛЮЧЕН"
    }
    return render(request, 'storage_control/pto_cabinet.html', context)

def index_vancouver(request):
    server_stat, created = ServerBalance.objects.get_or_create(id=1, defaults={'balance_rub': 0.00})
    cabinet = get_or_create_ezhik_charm(request)
    balance_rub = float(server_stat.balance_rub)
    return render(request, 'storage_control/miro_monolith.html', {
        'server_balance_rub': f"{balance_rub:,.2f}",
        'market_status': "КОНТУР АКТИВЕН // СЛОЙ_0 ОПЕЧАТАН",
        'user_cabinet': cabinet
    })

def capsule_time_vault(request):
    cabinet = get_or_create_ezhik_charm(request)
    video_list = EzhikVideoVault.objects.filter(is_approved_by_ezhik=True).order_by('-created_at')[:5]
    return render(request, 'storage_control/capsule.html', {'user_cabinet': cabinet, 'videos': video_list})

def upload_video_to_vault_api(request): return JsonResponse({'status': 'success'})
def push_video_to_telegram_action_api(request, video_id): return JsonResponse({'status': 'success'})
def send_to_stream_api(request): return JsonResponse({'status': 'success'})
def live_stream_dashboard_api(request): return JsonResponse({'stream': []})
def add_to_cart_api(request, product_id): return JsonResponse({'status': 'success'})
def checkout_sbp_payment_api(request): return JsonResponse({'status': 'paid'})
def save_vhd_journal_record(request): return JsonResponse({'status': 'success'})
def neuro_radar_dashboard(request): return render(request, 'storage_control/neuro_radar.html')
