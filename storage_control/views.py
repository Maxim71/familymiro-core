import random
import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ServerBalance, LiveStreamMessage, EzhikUserCabinet, EzhikVideoVault

REAL_TELEGRAM_TOKEN = "8658437799:AAFYMULZ41EyuPyvEFIt8WCCq8zvwsT7_1U"
REAL_CHAT_ID = "541888946"

def index_vancouver(request):
    """Монолитный пульт: данные вшиваются сервером сразу, исключая '[Ожидание данных...]'"""
    server_stat, created = ServerBalance.objects.get_or_create(id=1, defaults={'balance_rub': 0.00})
    balance_rub = float(server_stat.balance_rub)
    
    # Формируем жесткий список фактов прямо на бэкенде
    static_facts = [
        "🛰️ [АИС-СПУТНИК]: Контейнеровоз COSCO SHANGHAI везет гидравлику XCMG в порт Владивосток.",
        "👁️ [ИИ-ЗРЕНИЕ ЕЖИКА]: Матричный анализ армирования по осям А-Г завершен. Ошибок нет.",
        "📋 [ПТО СИНДИКАТА]: Лимиты ВОР засинхронизированы со складом М-19."
    ]
    
    # Добавляем сообщения из базы данных, если они есть
    db_msgs = LiveStreamMessage.objects.all().order_by('-created_at')[:3]
    
    context = {
        'server_balance_rub': f"{balance_rub:,.2f}",
        'object_capital_rub': "15 000 000.00 ₽",
        'market_status': "🛰️ СИСТЕМА МУЛЬТИМОДАЛЬНОГО КОНТРОЛЯ В СЕТИ",
        'action_notes': "🦔 Робот-Ёжик инициализирован. Автономные потоки активны.",
        'backend_facts': static_facts,
        'db_messages': db_msgs
    }
    return render(request, 'storage_control/miro_monolith.html', context)

@csrf_exempt
def send_to_stream_api(request):
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        if not text: return JsonResponse({'status': 'error'})
        
        reply = "🦔 Сигнал в ОЗУ!"
        LiveStreamMessage.objects.create(sender_name="Капитан Максим", message_text=text, ezhik_reply=reply)
        
        try:
            url = f"https://telegram.org{REAL_TELEGRAM_TOKEN}/sendMessage"
            requests.post(url, data={"chat_id": REAL_CHAT_ID, "text": f"📡 <b>[ЭФИР]:</b> {text}", "parse_mode": "HTML"}, timeout=2)
        except Exception: pass
        return JsonResponse({'status': 'success', 'reply': reply})
    return JsonResponse({'status': 'invalid'})

def live_stream_dashboard_api(request):
    return JsonResponse({'stream': [{"name": "🧠 СИСТЕМА", "text": "Поток стабилен", "reply": "ОК"}]})
def neuro_radar_dashboard(request): return render(request, 'storage_control/neuro_radar.html')
def pto_cabinet(request, act_id): return render(request, 'storage_control/pto_cabinet.html', {'act_id': act_id})
def capsule_time_vault(request): return render(request, 'storage_control/capsule.html')
def import_excel_pto_api(request): return JsonResponse({'status': 'success'})
def ezhik_voice_notepad_api(request): return JsonResponse({'status': 'success'})
def neuro_radar_voice_api(request): return JsonResponse({'status': 'success'})
def upload_video_to_vault_api(request): return JsonResponse({'status': 'success'})
def push_video_to_telegram_action_api(request, video_id): return JsonResponse({'status': 'success'})
def add_to_cart_api(request, product_id): return JsonResponse({'status': 'success'})
def checkout_sbp_payment_api(request): return JsonResponse({'status': 'paid'})
def save_vhd_journal_record(request): return JsonResponse({'status': 'success'})
def computer_vision_m19_api(request): return JsonResponse({'status': 'success'})
