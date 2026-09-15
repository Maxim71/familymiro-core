import random
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone
from .models import MaterialM15Invoice, WarehouseStock, ItrProrabTest, LiveStreamMessage, ConstructionObject

def index_vancouver(request):
    """Главный sci-fi пульт управления Legenda Mobile"""
    return render(request, 'storage_control/miro_monolith.html')

def pto_cabinet(request, act_id):
    """Кабинет ПТО"""
    return render(request, 'storage_control/pto_cabinet.html')

def save_vhd_journal_record(request):
    """Журнал ВХД: Автоматизация АОСР по фотоотчётам"""
    if request.method == 'POST':
        prorab = request.POST.get('prorab_name', 'Прораб Линии').strip()
        stage = request.POST.get('work_stage', 'Общестроительные работы').strip()
        is_delayed = request.POST.get('delay') == 'True'
        defects = request.POST.get('defects_text', '').strip()
        
        has_defect = is_delayed or defects
        msg_status = "🚨 ДЕФЕКТНАЯ ВЕДОМОСТЬ ВЫПИСАНА!" if has_defect else "✅ ЖУРНАЛ ВХД СТАБИЛЕН! АОСР оформлен!"

        ItrProrabTest.objects.create(
            prorab_name=prorab, work_stage=stage,
            delivery_delay_detected=is_delayed, visible_defects_notes=defects,
            defect_sheet_issued=has_defect
        )
        return JsonResponse({'status': 'success', 'message': msg_status, 'defect_sheet': has_defect})
    return JsonResponse({'status': 'invalid'})

def live_stream_dashboard_api(request):
    """Выгрузка сообщений живого эфира"""
    messages_list = LiveStreamMessage.objects.all().order_by('-created_at')[:5]
    data = [{'name': m.sender_name, 'text': m.message_text, 'reply': m.ezhik_reply} for m in messages_list]
    return JsonResponse({'stream': data})

def send_to_stream_api(request):
    """Прием сообщений в стерео-поток"""
    if request.method == 'POST':
        name = request.POST.get('name', 'Прораб ИТР').strip()
        text = request.POST.get('text', '').strip()
        reply_text = "🦔 [ЁЖИК]: Поток стерилен. Сигнал перехвачен в Эскиз Памяти."
        
        LiveStreamMessage.objects.create(sender_name=name, message_text=text, ezhik_reply=reply_text)
        return JsonResponse({'status': 'success', 'reply': reply_text})
    return JsonResponse({'status': 'invalid'})

def add_to_cart_api(request, product_id):
    """Пополнение Капсулы донатов"""
    return JsonResponse({'status': 'success', 'cart_count': random.randint(1, 10)})

def checkout_sbp_payment_api(request):
    """Авторизация инвойса СБП INV-ALFA-288003"""
    return JsonResponse({'status': 'paid', 'message': '💳 [СБП ШЛЮЗ]: 15,000,000.00 ₽ переведены в Капсулу Вечности!'})

def neuro_radar_dashboard(request):
    """Нейро-Радар логистики рейсов"""
    return render(request, 'storage_control/neuro_radar.html')

def capsule_time_vault(request):
    """Капсула времени до 2059 года"""
    return render(request, 'storage_control/capsule.html')
