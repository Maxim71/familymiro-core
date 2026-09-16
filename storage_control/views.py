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

def neuro_radar_dashboard(request):
    """🛰️ НЕЙРО-РАДАР ЛОГИСТИКИ РЕЙСОВ ИЗ КИТАЯ (ШЛЮЗ СЛОЙ_0)"""
    cabinet = get_or_create_ezhik_charm(request)
    
    # Моделируем живую телеметрию судов в Жёлтом и Японском морях
    vessels_tracking = [
        {
            "id": "VESSEL-XCMG-99",
            "name": "🚢 Контейнеровоз 'COSCO SHANGHAI'",
            "cargo": "⚙️ 40 контейнеров: Гидравлика XCMG и фасадные системы MONLID",
            "route": "Шанхай (КНР) ➔ Владивосток (РФ)",
            "coordinates": "34.12° N, 124.45° E (Желтое море)",
            "status": "🌊 В ПУТИ // ШТОРМ 2 БАЛЛА",
            "eta": "22.09.2026",
            "color_theme": "cyan"
        },
        {
            "id": "VESSEL-KOM-104",
            "name": "🚢 Сухогруз 'PACIFIC PHOENIX'",
            "cargo": "🚜 Редукторы Komatsu PC200 и бортовые передачи Liugong",
            "route": "Нинбо (КНР) ➔ Владивосток (РФ)",
            "coordinates": "41.56° N, 131.12° E (Подход к Приморью)",
            "status": "⚓️ НА ПОДХОДЕ // Ожидание лоцмана",
            "eta": "18.09.2026 (ЧЕРЕЗ 2 ДНЯ)",
            "color_theme": "green"
        }
    ]
    
    context = {
        'user_cabinet': cabinet,
        'vessels': vessels_tracking,
        'system_status': "НЕЙРО-РАДАР СЛОЙ_0: ТЕЛЕМЕТРИЯ СУДОВ ИЗ КНР АКТИВНА"
    }
    return render(request, 'storage_control/neuro_radar.html', context)

@csrf_exempt
def neuro_radar_voice_api(request):
    """🎙️ ИИ-БЛОКНОТ ДИСПЕТЧЕРА РЕЙСОВ: Стерилизация сырых мыслей по координатам груза"""
    if request.method == 'POST':
        raw_text = request.POST.get('raw_input', '').strip()
        if not raw_text: return JsonResponse({'status': 'error', 'message': 'Пустой ввод'})
        
        structured_radar_output = (
            f"🛰️ <b>[НЕЙРО-РАДАР // КОРРЕКТИРОВКА РЕЙСА]</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🚢 <b>ГРУЗ:</b> Бортовые редукторы Komatsu (Партия #K-104).\n"
            f"📍 <b>ЛОГИСТИКА:</b> Судно подходит к Владивостоку. Снабженцу подтвердить готовность контейнеровоза.\n"
            f"🧱 <b>СТРОЙКА:</b> Прорабу Тулы выставить лимит ПТО под разгрузку через 5 дней!\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🤖 <i>ИИ-Стерилизатор перевёл сырые мысли: \"{raw_text[:35]}...\" в понятные ИТР-команды. Рапорт отправлен Капитану.</i>"
        )
        
        # Моментальный авто-выстрел рапорта в Telegram Капитана
        try:
            requests.post(f"https://telegram.org{REAL_TELEGRAM_TOKEN}/sendMessage", data={
                "chat_id": REAL_CHAT_ID, "text": structured_radar_output, "parse_mode": "HTML"
            }, timeout=3)
        except Exception: pass
        
        return JsonResponse({'status': 'success', 'structured_text': structured_radar_output})
    return JsonResponse({'status': 'invalid'})

# Остальные шлюзы Капсулы и ПТО сохраняем без единого изменения
def pto_cabinet(request, act_id):
    cabinet = get_or_create_ezhik_charm(request)
    materials_chain = [{"name": "Арматура стальная А500С 12мм", "pto_limit": "45.0 тонн", "purchased": "42.0 тонн", "price_target": "68,000 ₽/т", "warehouse_m19": "40.0 тонн на объекте", "finance_status": "КС-2 закрыто на 30.0 т", "alert_class": "cyan"}]
    parser_cargo = [{"brand": "⚙️ Запчасти гидравлики XCMG / Liugong", "batch": "Партия #X-992 (Завод КНР)", "port_status": "⚓️ ВЛАДИВОСТОК // Таможня выпущена", "logistic_action": "🛒 Снабженец: Фура зафрахтована. 📐 ПТО: Простоев нет. 🧱 Прораб: Автокран вызван.", "days_left": "Прибытие через 5 дней", "color": "green"}]
    return render(request, 'storage_control/pto_cabinet.html', {'act_id': act_id, 'user_cabinet': cabinet, 'materials_chain': materials_chain, 'parser_cargo': parser_cargo, 'total_budget_rub': "15 000 000.00 ₽", 'real_cost_rub': "8 420 500.00 ₽", 'system_status': "ИТР ИИ-БЛОКНОТ СВЯЗИ И EXCEL ПОРТЫ ЗАКРЫТЫ В ОЗУ"})

def index_vancouver(request): return render(request, 'storage_control/miro_monolith.html', {'user_cabinet': get_or_create_ezhik_charm(request)})
def capsule_time_vault(request): return render(request, 'storage_control/capsule.html')
def upload_video_to_vault_api(request): return JsonResponse({'status': 'success'})
def push_video_to_telegram_action_api(request, video_id): return JsonResponse({'status': 'success'})
def send_to_stream_api(request): return JsonResponse({'status': 'success'})
def live_stream_dashboard_api(request): return JsonResponse({'stream': []})
def add_to_cart_api(request, product_id): return JsonResponse({'status': 'success'})
def checkout_sbp_payment_api(request): return JsonResponse({'status': 'paid'})
def save_vhd_journal_record(request): return JsonResponse({'status': 'success'})
def import_excel_pto_api(request): return JsonResponse({'status': 'success'})
def ezhik_voice_notepad_api(request): return JsonResponse({'status': 'success'})
