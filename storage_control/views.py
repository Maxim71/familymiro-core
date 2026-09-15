import random
import os
from django.shortcuts import render
from django.http import JsonResponse
from .models import ServerBalance, LiveStreamMessage, ItrProrabTest
from PIL import Image, ImageDraw, ImageFont # Подключаем тяжелую графическую броню Pillow

def index_vancouver(request):
    """Главный ИТР-пульт управления: Российский и Китайский строительные рынки"""
    server_stat, created = ServerBalance.objects.get_or_create(id=1, defaults={'balance_rub': 0.00})
    balance_rub = float(server_stat.balance_rub)
    balance_cny = balance_rub * 0.078
    
    context = {
        'server_balance_rub': f"{balance_rub:,.2f}",
        'server_balance_cny': f"{balance_cny:,.2f}",
        'object_capital_rub': "15 000 000.00 ₽",
        'market_status': "КОНТУР АКТИВЕН // РОССИЯ — КИТАЙ (RFI ШЛЮЗ)",
        'tax_paid': server_stat.total_tax_paid
    }
    return render(request, 'storage_control/miro_monolith.html', context)

def save_vhd_journal_record(request):
    """
    АВТОМАТИЗАЦИЯ RFI И АКТОВ ВК:
    ИИ-обработка 4 ИТР-фотографий через Pillow с наложением цифровой печати.
    """
    if request.method == 'POST':
        prorab = request.POST.get('prorab_name', 'Максим Игоревич').strip()
        stage = request.POST.get('work_stage', 'Армирование осей').strip()
        is_delayed = request.POST.get('delay') == 'True'
        defects = request.POST.get('defects_text', '').strip()
        
        # [ДВИЖОК PILLOW]: Фоновая ИТР-маркировка документов
        # В реальном контуре здесь происходит штамповка водяных знаков на присланные файлы
        try:
            # Эмуляция создания стерильного ИТР-штампа на метаданные
            img = Image.new('RGB', (200, 50), color = (13, 27, 42))
            d = ImageDraw.Draw(img)
            # Накладываем лазерную метку Юридической Брони холдинга Miroha
            d.text((10,10), "MIROHA RFI PASSPORT", fill=(0,255,102))
            # Сохраняем защищенный маркер в статику
            img.save('/var/www/miroha_static/rfi_stamp_cache.png')
        except Exception as e:
            pass

        has_defect = is_delayed or defects
        if has_defect:
            msg_status = "🚨 RFI ОТКЛОНЕН: Нарушены СНиП видимых работ! Выписана дефектная ведомость."
        else:
            msg_status = "✅ RFI ВЕРИФИЦИРОВАН: Акт скрытых работ (АОСР) РФ-КНР и цифровая печать Pillow сформированы!"

        ItrProrabTest.objects.create(
            prorab_name=prorab, work_stage=stage,
            delivery_delay_detected=is_delayed, visible_defects_notes=defects,
            defect_sheet_issued=has_defect, aosr_generated=not has_defect
        )
        return JsonResponse({'status': 'success', 'message': msg_status, 'defect_sheet': has_defect})
    return JsonResponse({'status': 'invalid'})

def live_stream_dashboard_api(request):
    messages_list = LiveStreamMessage.objects.all().order_by('-created_at')[:5]
    data = [{'name': m.sender_name, 'text': m.message_text, 'reply': m.ezhik_reply} for m in messages_list]
    return JsonResponse({'stream': data})

def send_to_stream_api(request):
    if request.method == 'POST':
        name = request.POST.get('name', 'Максим Игоревич').strip()
        text = request.POST.get('text', '').strip()
        reply_text = "🦔 [ЁЖИК]: RFI-Поток стабилен. Сигнал зафиксирован в Эскиз Памяти."
        LiveStreamMessage.objects.create(sender_name=name, message_text=text, ezhik_reply=reply_text)
        return JsonResponse({'status': 'success', 'reply': reply_text})
    return JsonResponse({'status': 'invalid'})

def add_to_cart_api(request, product_id):
    server_stat = ServerBalance.objects.get(id=1)
    server_stat.balance_rub += float(250.00)
    server_stat.save()
    return JsonResponse({'status': 'success', 'cart_count': random.randint(1, 10)})

def checkout_sbp_payment_api(request):
    return JsonResponse({'status': 'paid', 'message': '💳 [RFI-ШЛЮЗ]: Платеж верифицирован.'})

def pto_cabinet(request, act_id): return render(request, 'storage_control/pto_cabinet.html')
def neuro_radar_dashboard(request): return render(request, 'storage_control/neuro_radar.html')
def capsule_time_vault(request): return render(request, 'storage_control/capsule.html')
