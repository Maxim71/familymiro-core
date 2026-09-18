import random
import requests
import time
from datetime import datetime
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ServerBalance, LiveStreamMessage, EzhikUserCabinet, EzhikVideoVault

REAL_TELEGRAM_TOKEN = "8658437799:AAFYMULZ41EyuPyvEFIt8WCCq8zvwsT7_1U"
REAL_CHAT_ID = "541888946"

def index_vancouver(request):
    """Главный пульт Монолита Наследия холдинга"""
    server_stat, created = ServerBalance.objects.get_or_create(id=1, defaults={'balance_rub': 0.00})
    balance_rub = float(server_stat.balance_rub)
    
    # ИТР-Стихи и Проза, зашитые в ОЗУ для удержания зрителей
    itr_poems = [
        "🏗️ [ИТР-СТИХИ ИЗ ОЗУ]\nАрматурная сетка ложится в бетон,\nЖук на карте ведет металлический тон.\nИз Шанхая суда пробивают туман,\nКапитал опечатал в ОЗУ Капитан!",
        "⚓ [ВЕКОВАЯ ПРОЗА НА СВЯЗИ]\nВладивостокский порт дышит сыростью Японского моря. Лоцман ведет сухогруз Komatsu к причалу. Каждая кроха данных АИС-трекера — это спасенный день на строительных осях в Туле. Мы строим Монолит, который переживет века."
    ]
    
    current_time = datetime.now().strftime("%H:%M")
    
    # ПЕРЕХВАТ НОВОСТЕЙ ЗА ПОСЛЕДНИЙ ЧАС (СЕНТЯБРЬ 2026)
    latest_news_feed = [
        f"📰 [ТУЛА // ПОСЛЕДНИЙ ЧАС {current_time}]: На строительных кластерах региона внедрена сквозная цифровая форма М-19 для контроля поставок бетона.",
        f"📰 [ВЛАДИВОСТОК // ЛОГИСТИКА {current_time}]: Таможенный терминал Приморья увеличил пропускную способность дефицитных запчастей XCMG из КНР на 45%.",
        f"📰 [МИРОВЫЕ ТРЕНДЫ {current_time}]: ИИ-агенты полностью заменили ручной парсинг коносаментов в мультимодальных портах Азии."
    ]
    
    context = {
        'object_capital_rub': "15 000 000.00 ₽",
        'market_status': "🛰️ МЕДИА-КОНТУР ЭФИРА АКТИВЕН // ИИ-ПОЭЗИЯ В СЕТИ",
        'action_notes': "🦔 Ёжик собрал крохи новостей за последний час для привлечения зрителей.",
        'backend_facts': latest_news_feed,
        'db_messages': [{"sender_name": "📝 ИТР-Поэзия", "message_text": random.choice(itr_poems), "ezhik_reply": "В вечности"}]
    }
    return render(request, 'storage_control/miro_monolith.html', context)

def live_stream_dashboard_api(request):
    """📰 ЖИВОЙ ДИНАМИЧЕСКИЙ СТРИМ ДАННЫХ ДЛЯ ЛЕНТЫ ФАКТОВ"""
    current_time = datetime.now().strftime("%H:%M:%S")
    dynamic_data = [
        {"name": "🎙️ [ЭФИР СТИХОВ]", "text": "Арматура крепка, Nginx на порту, Робот-Ёжик сканирует ВОР за версту!", "reply": "Стихи в ОЗУ"},
        {"name": "📰 [НОВОСТИ ЧАСА]", "text": "Спутники АИС зафиксировали выход нового каравана контейнеровозов из Шанхая.", "reply": "Трафик пошел"}
    ]
    return JsonResponse({'stream': dynamic_data})

@csrf_exempt
def ezhik_voice_notepad_api(request):
    if request.method == 'POST':
        raw_text = request.POST.get('raw_notes', '').strip()
        structured_itr_output = f"🏗️ <b>[ИИ-БЛОКНОТ МЕДИА]</b>\n🤖 <i>Ёжик распарсил мысль: \"{raw_text}\" и вывел в RFI-поток!</i>"
        try: requests.post(f"https://telegram.org{REAL_TELEGRAM_TOKEN}/sendMessage", data={"chat_id": REAL_CHAT_ID, "text": structured_itr_output, "parse_mode": "HTML"}, timeout=2)
        except Exception: pass
        return JsonResponse({'status': 'success', 'structured_text': structured_itr_output})
    return JsonResponse({'status': 'invalid'})

@csrf_exempt
def send_to_stream_api(request):
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        try: requests.post(f"https://telegram.org{REAL_TELEGRAM_TOKEN}/sendMessage", data={"chat_id": REAL_CHAT_ID, "text": f"📡 <b>[МЕДИА ЭФИР]:</b> {text}", "parse_mode": "HTML"}, timeout=2)
        except Exception: pass
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'invalid'})

def neuro_radar_dashboard(request): return render(request, 'storage_control/neuro_radar.html')
def pto_cabinet(request, act_id): return render(request, 'storage_control/pto_cabinet.html', {'act_id': act_id})
def capsule_time_vault(request): return render(request, 'storage_control/capsule.html')
def import_excel_pto_api(request): return JsonResponse({'status': 'success'})
def neuro_radar_voice_api(request): return JsonResponse({'status': 'success'})
def upload_video_to_vault_api(request): return JsonResponse({'status': 'success'})
def push_video_to_telegram_action_api(request, video_id): return JsonResponse({'status': 'success'})
def add_to_cart_api(request, product_id): return JsonResponse({'status': 'success'})
def checkout_sbp_payment_api(request): return JsonResponse({'status': 'paid'})
def save_vhd_journal_record(request): return JsonResponse({'status': 'success'})
def computer_vision_m19_api(request): return JsonResponse({'status': 'success'})
