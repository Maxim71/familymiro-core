import random
import pyotp
from django.shortcuts import render
from django.http import JsonResponse
from .models import ServerBalance, LiveStreamMessage, ItrProrabTest, EzhikUserCabinet

CAPTAIN_SECRET = "M32MIROHACRE2059VAULTTANGERINE55"

def get_or_create_ezhik_charm(request):
    """Фоновый ИИ-движок Шарма Ёжика: Автоматическое создание аккаунта и стиля"""
    if not request.session.session_key:
        request.session.create()
    s_key = request.session.session_key
    
    moba_names = ["Мастер Осей", "Вековой Хроникер", "Инфлюенсер Наследия", "RFI Диспетчер", "Продюсер Эфира"]
    moba_styles = ["cyan", "pink", "green", "gold"]
    
    cabinet, created = EzhikUserCabinet.objects.get_or_create(
        session_key=s_key,
        defaults={
            'assigned_name': f"{random.choice(moba_names)} №{random.randint(100, 999)}",
            'moba_style_preference': random.choice(moba_styles),
            'user_country': "Россия"
        }
    )
    return cabinet

def index_vancouver(request):
    """Главный ИТР-пульт управления: Адаптация под личный стиль Ёжика"""
    server_stat, created = ServerBalance.objects.get_or_create(id=1, defaults={'balance_rub': 0.00})
    cabinet = get_or_create_ezhik_charm(request)
    
    balance_rub = float(server_stat.balance_rub)
    balance_cny = balance_rub * 0.078
    balance_kpw = balance_rub * 9.87
    
    action_notes = f"🦔 [ШАРМ ЁЖИКА]: Приветствую, {cabinet.assigned_name}! Я настроил платформу под твой личный неоновый стиль '{cabinet.moba_style_preference}'. Контур стабилен."

    context = {
        'server_balance_rub': f"{balance_rub:,.2f}",
        'server_balance_cny': f"{balance_cny:,.2f}",
        'server_balance_kpw': f"{balance_kpw:,.2f}",
        'object_capital_rub': "15 000 000.00 ₽",
        'market_status': "КОНТУР АКТИВЕН // PROTOCOL GIT-GATE-РТО",
        'tax_paid': server_stat.total_tax_paid,
        'user_cabinet': cabinet,
        'action_notes': action_notes
    }
    return render(request, 'storage_control/miro_monolith.html', context)

def send_to_stream_api(request):
    if request.method == 'POST':
        name = request.POST.get('name', 'Прораб ИТР').strip()
        text = request.POST.get('text', '').strip()
        reply_text = "🦔 [ЁЖИК]: Сигнал зафиксирован в Глобальный Эскиз Памяти."
        LiveStreamMessage.objects.create(sender_name=name, message_text=text, ezhik_reply=reply_text)
        return JsonResponse({'status': 'success', 'reply': reply_text})
    return JsonResponse({'status': 'invalid'})

def live_stream_dashboard_api(request):
    """Исправленный ИИ-метод: Сортировка через order_by без падений"""
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
def capsule_time_vault(request): return render(request, 'storage_control/capsule.html')
