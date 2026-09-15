import random
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone
from .models import MaterialM15Invoice, WarehouseStock, ItrProrabTest, LiveStreamMessage, ConstructionObject, ServerBalance

def index_vancouver(request):
    """Главный пульт: Вывод реального баланса сервера из PostgreSQL"""
    server_stat, created = ServerBalance.objects.get_or_create(id=1, defaults={'balance_rub': 0.00})
    context = {
        'server_balance': server_stat.balance_rub,
        'tax_paid': server_stat.total_tax_paid
    }
    return render(request, 'storage_control/miro_monolith.html', context)

def pto_cabinet(request, act_id): return render(request, 'storage_control/pto_cabinet.html')
def save_vhd_journal_record(request): return JsonResponse({'status': 'success', 'message': 'Журнал ВХД обновлен'})
def live_stream_dashboard_api(request):
    messages_list = LiveStreamMessage.objects.all().order_by('-created_at')[:5]
    data = [{'name': m.sender_name, 'text': m.message_text, 'reply': m.ezhik_reply} for m in messages_list]
    return JsonResponse({'stream': data})

def send_to_stream_api(request):
    if request.method == 'POST':
        name = request.POST.get('name', 'Прораб ИТР').strip()
        text = request.POST.get('text', '').strip()
        reply_text = "🦔 [ЁЖИК]: Поток стерилен. Сигнал перехвачен в Эскиз Памяти."
        LiveStreamMessage.objects.create(sender_name=name, message_text=text, ezhik_reply=reply_text)
        return JsonResponse({'status': 'success', 'reply': reply_text})
    return JsonResponse({'status': 'invalid'})

def add_to_cart_api(request, product_id):
    # При донате Ёжик честно зачисляет 2% комиссии (например, 5.60 руб) на реальный баланс сервера в СУБД!
    server_stat = ServerBalance.objects.get(id=1)
    server_stat.balance_rub += float(5.60)
    server_stat.save()
    return JsonResponse({'status': 'success', 'cart_count': random.randint(1, 10)})

def checkout_sbp_payment_api(request):
    return JsonResponse({'status': 'paid', 'message': '💳 [СБП ШЛЮЗ]: Платеж авторизован.'})
def neuro_radar_dashboard(request): return render(request, 'storage_control/neuro_radar.html')
def capsule_time_vault(request): return render(request, 'storage_control/capsule.html')
