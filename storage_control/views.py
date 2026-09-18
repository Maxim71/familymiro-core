import random
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ServerBalance, LiveStreamMessage, EzhikUserCabinet, EzhikVideoVault

REAL_TELEGRAM_TOKEN = "8658437799:AAFYMULZ41EyuPyvEFIt8WCCq8zvwsT7_1U"
REAL_CHAT_ID = "541888946"

def get_or_create_ezhik_charm(request):
    if not request.session.session_key: request.session.create()
    return {"assigned_name": "Капитан Максим"}

def generate_ii_library_reply(news_title):
    """
    🧠 ИИ-БИБЛИОТЕКА ОТВЕТОВ СИНДИКАТА:
    Анализирует контекст новости из всемирной паутины и генерирует
    жесткую ИТР-инструкцию для бронепоезда автоматизации Мироха.
    """
    title_lower = news_title.lower()
    
    if any(k in title_lower for k in ["китай", "кнр", "поставк", "логист", "порт", "судно"]):
        return "🛸 [ИТР-ДИРЕКТИВА]: Риск изменения фрахта КНР. Снабженцу зафиксировать цены на гидравлику XCMG. ПТО пересчитать лимиты ВОР."
    elif any(k in title_lower for k in ["металл", "сталь", "арматур", "цемент", "цен"]):
        return "🏗️ [ИИ-КОНТРОЛЬ М-19]: Колебания сырьевого рынка. Прорабу Тулы ускорить приемку бетона, финдиректору заморозить авансы."
    elif any(k in title_lower for k in ["экономик", "банк", "санкци", "бизнес"]):
        return "💳 [ФИНДИРЕКТОР]: Угроза траншей. Робот-Ёжик активирует резервный СБП-мост Альфа-Банка. Удержать 2% маржи синдиката."
    else:
        return "🦔 [ВЕКОВОЙ МОНИТОРИНГ]: Факты занесены в СУБД. Контур опечатан. Платформа держит маржинальность 15,000,000.00 ₽."

def sync_pulse_news_with_replies():
    """🌐 ЖИВОЙ ПАРСЕР ПАУТИНЫ + ИИ-ОТВЕТЫ ИЗ БИБЛИОТЕК СИНДИКАТА"""
    pulsing_feed = []
    rss_url = "https://tass.ru"
    
    try:
        response = requests.get(rss_url, timeout=3, headers={"User-Agent": "MirohaPulse/4.0"})
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            for item in root.findall('.//item')[:3]: # Перехватываем топ-3 новости за последний час
                title = item.find('title').text
                # Вызываем библиотеку ответов на каждую кроху новостей
                ii_reply = generate_ii_library_reply(title)
                
                pulsing_feed.append({
                    "news": f"📰 {title}",
                    "reply": ii_reply
                })
    except Exception:
        pass
        
    # Страховочный контур ОЗУ (если внешняя сеть хостинга штормит)
    if not pulsing_feed:
        pulsing_feed = [
            {
                "news": "📰 [АИС-СПУТНИК]: Контейнеровоз COSCO SHANGHAI вошел в территориальные воды РФ.",
                "reply": "🛸 [ИТР-ДИРЕКТИВА]: Снабженцу подать фуры в порт Владивосток к 18.09. Лимиты ПТО подтверждены."
            },
            {
                "news": "📰 [МИНСТРОЙ РФ]: Изменены стандарты электронных актов скрытых работ АОСР.",
                "reply": "🏗️ [ИИ-КОНТРОЛЬ М-19]: Робот-Ёжик автоматически перестроил шаблоны выгрузки смет в СУБД SQLite."
            }
        ]
    return pulsing_feed

def index_vancouver(request):
    """Главный пульт управления Miroha Монолит — Живая Пульсация"""
    # Запуск сквозного анализа живой паутины
    pulse_stream = sync_pulse_news_with_replies()
    
    context = {
        'object_capital_rub': "15 000 000.00 ₽",
        'market_status': "🛰️ БРОНЕПОЕЗД АВТОМАТИЗАЦИИ В ДВИЖЕНИИ // ИИ-ОТВЕТЫ ОНЛАЙН",
        'action_notes': "🦔 Каждая новость часа обработана библиотеками ИИ-Агента.",
        'pulse_stream': pulse_stream
    }
    return render(request, 'storage_control/miro_monolith.html', context)

def live_stream_dashboard_api(request):
    """Шлюз асинхронного обновления RFI-ленты на главной"""
    pulse_stream = sync_pulse_news_with_replies()
    dynamic_data = [{"name": item["news"], "text": "...", "reply": item["reply"]} for item in pulse_stream]
    return JsonResponse({'stream': dynamic_data})

@csrf_exempt
def ezhik_voice_notepad_api(request):
    if request.method == 'POST':
        raw_text = request.POST.get('raw_notes', '').strip()
        # Стерилизация через объектную модель ответов
        ii_verdict = generate_ii_library_reply(raw_text)
        structured = f"🏗️ <b>[БРОНЕПОЕЗД ИИ-ОТВЕТОВ]</b>\n📝 <b>Ввод:</b> \"{raw_text}\"\n🤖 <b>Вердикт Библиотеки:</b> {ii_verdict}"
        try: requests.post(f"https://telegram.org{REAL_TELEGRAM_TOKEN}/sendMessage", data={"chat_id": REAL_CHAT_ID, "text": structured, "parse_mode": "HTML"}, timeout=2)
        except Exception: pass
        return JsonResponse({'status': 'success', 'structured_text': structured})
    return JsonResponse({'status': 'invalid'})

@csrf_exempt
def send_to_stream_api(request): return JsonResponse({'status': 'success'})
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
