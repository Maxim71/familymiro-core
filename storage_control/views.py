import random
import pyotp
from django.shortcuts import render
from django.http import JsonResponse
from .models import ServerBalance, LiveStreamMessage, ItrProrabTest

# Суверенный секретный ключ Капитана для Google Authenticator (запечатан навечно)
# Ты можешь отсканировать этот ключ в приложении Google Authenticator на телефоне
CAPTAIN_SECRET = "M32MIROHACRE2059VAULTTANGERINE55"

def index_vancouver(request):
    """Главный ИТР-пульт управления: Трехсторонний шлюз Россия — Китай — КНДР"""
    server_stat, created = ServerBalance.objects.get_or_create(id=1, defaults={'balance_rub': 0.00})
    balance_rub = float(server_stat.balance_rub)
    balance_cny = balance_rub * 0.078
    balance_kpw = balance_rub * 9.87
    
    context = {
        'server_balance_rub': f"{balance_rub:,.2f}",
        'server_balance_cny': f"{balance_cny:,.2f}",
        'server_balance_kpw': f"{balance_kpw:,.2f}",
        'object_capital_rub': "15 000 000.00 ₽",
        'market_status': "КОНТУР АКТИВЕН // PROTOCOL GIT-GATE-РТО",
        'tax_paid': server_stat.total_tax_paid
    }
    return render(request, 'storage_control/miro_monolith.html', context)

def capsule_time_vault(request):
    """
    РАСПРЕДЕЛЕННАЯ КАПСУЛА ВЕЧНОСТЬ:
    Интеграция с Google Authenticator. Закрытый вход по QR и TOTP коду.
    Пользователи из Италии и мира видят только форму отправки строк потомству.
    """
    is_captain = False
    error_msg = None
    
    # Проверяем, ввёл ли Капитан код двухфакторки из приложения Google Authenticator
    if request.method == 'POST' and 'totp_code' in request.POST:
        code = request.POST.get('totp_code', '').strip()
        totp = pyotp.TOTP(CAPTAIN_SECRET)
        
        if totp.verify(code):
            is_captain = True # Шлюз открыт, виза Капитана подтверждена!
        else:
            error_msg = "🚨 КРИПТО-ОШИБКА: Неверный код Google Authenticator! Доступ к таймеру опеки дочери заблокирован!"

    # Вековые послания от внешних пользователей (Италия, мир)
    global_messages = [
        {"author": "User из Милана, Италия", "text": "Salute! Запечатываю пожелание вечного процветания империи Miroha!"},
        {"author": "Инвестор Шанхай", "text": "Уважение Конструктору Максиму. Строки занесены в матрицу результатов."}
    ]
    
    from datetime import datetime
    target_date = datetime(2059, 5, 24, 0, 0, 0)
    time_delta = target_date - datetime.now()
    days_left = time_delta.days
    
    context = {
        'is_captain': is_captain,
        'error_msg': error_msg,
        'years': days_left // 365,
        'days': days_left % 365,
        'sbp_code': "INV-ALFA-288003",
        'global_messages': global_messages,
        # Ссылка на QR-код для генерации Капитанского ключа в Google Authenticator
        'qr_setup_url': f"https://qrserver.com{CAPTAIN_SECRET}%26issuer=MirohaPlatform"
    }
    return render(request, 'storage_control/capsule.html', context)

def send_to_stream_api(request):
    if request.method == 'POST':
        name = request.POST.get('name', 'Прораб ИТР').strip()
        text = request.POST.get('text', '').strip()
        reply_text = "🦔 [ЁЖИК]: Сигнал зафиксирован в Глобальный Эскиз Памяти."
        LiveStreamMessage.objects.create(sender_name=name, message_text=text, ezhik_reply=reply_text)
        return JsonResponse({'status': 'success', 'reply': reply_text})
    return JsonResponse({'status': 'invalid'})

def live_stream_dashboard_api(request):
    messages_list = LiveStreamMessage.objects.all().order_by('-created_at')[:5]
    data = [{'name': m.sender_name, 'text': m.message_text, 'reply': m.ezhik_reply} for m in messages_list]
    return JsonResponse({'stream': data})

def add_to_cart_api(request, product_id):
    server_stat = ServerBalance.objects.get(id=1)
    server_stat.balance_rub += float(250.00)
    server_stat.save()
    return JsonResponse({'status': 'success', 'cart_count': random.randint(1, 10)})

def checkout_sbp_payment_api(request): return JsonResponse({'status': 'paid'})
def pto_cabinet(request, act_id): return render(request, 'storage_control/pto_cabinet.html')
def save_vhd_journal_record(request): return JsonResponse({'status': 'success'})
def neuro_radar_dashboard(request): return render(request, 'storage_control/neuro_radar.html')
