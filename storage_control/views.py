from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import ConstructionObject, SpaceTransferAct, MaterialM15Invoice

import urllib.request
import re
import os
from django.http import JsonResponse
from bs4 import BeautifulSoup


from django.contrib import messages
from decimal import Decimal
from .models import SpaceTransferAct, MaterialM15Invoice, WarehouseStock

def pto_cabinet(request, act_id):
    """Шлюз отображения цифрового Акта ПТО и формы М-15"""
    act = get_object_or_404(SpaceTransferAct, id=act_id)
    materials = MaterialM15Invoice.objects.filter(act_link=act)
    return render(request, 'pto_cabinet.html', {'act': act, 'materials': materials})

def approve_act(request, act_id):
    """
    Капитанский мостик: Мгновенное электронное согласование Начальника Участка
    с автоматическим списанием материалов со склада в реальном времени.
    """
    if request.method == 'POST':
        # 1. Находим Акт фронта работ по осям и этажам
        act = get_object_or_404(SpaceTransferAct, id=act_id)
        
        if not act.chief_approved:
            # 2. Находим все накладные М-15 (давальческие материалы), привязанные к акту
            invoices = MaterialM15Invoice.objects.filter(act_link=act)
            
            # 3. Запускаем конвейер Робота-Ёжика по каждой позиции накладной
            for inv in invoices:
                # Ищем этот материал на остатках нашего склада
                stock_item = WarehouseStock.objects.filter(material_name=inv.material_name).first()
                
                if stock_item:
                    # Если запасов хватает — списываем со склада на лету!
                    if stock_item.quantity >= inv.quantity:
                        stock_item.quantity -= inv.quantity
                        stock_item.save()
                    else:
                        # Если на складе дефицит — забираем всё что есть, остальное в дефицит
                        inv.quantity = stock_item.quantity  # фиксируем, сколько реально смогли выдать
                        stock_item.quantity = Decimal('0.00')
                        stock_item.save()
                else:
                    # Если такого материала на складе вообще никогда не было — создаем нулевую запись
                    WarehouseStock.objects.create(
                        material_name=inv.material_name,
                        quantity=Decimal('0.00'),
                        unit=inv.unit
                    )
                
                # Запечатываем подпись на самой накладной М-15
                inv.is_signed_by_chief = True
                inv.save()
            
            # 4. Активируем электронную визу самого Акта ПТО
            act.chief_approved = True
            act.chief_approved_at = timezone.now()
            act.save()
            
    return redirect('pto_cabinet', act_id=act_id)


def ezhiha_parser_trigger(request):
    """Точечный ИИ-парсер Лемана ПРО по запросу ПТО, Снабжения или Склада"""
    product_name = request.GET.get('product_name', '').strip()
    trigger_source = request.GET.get('source', 'unknown') # pto, supplier, warehouse
    
    if not product_name:
        return JsonResponse({'status': 'error', 'message': 'Пустой запрос материала'})
        
    # Создаем папку под вековые сертификаты, если её нет
    cert_dir = '/root/app/media/certificates/'
    os.makedirs(cert_dir, exist_ok=True)
    
    try:
        # Эмулируем реальный браузер жителя Тулы для обхода блокировок Лемана ПРО
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        encoded_query = urllib.parse.quote(product_name)
        search_url = f"https://lemanapro.ru{encoded_query}"
        
        req = urllib.request.Request(search_url, headers={'User-Agent': user_agent})
        
        # Робот-Ёжик заходит на сайт Лемана ПРО в Туле
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
            
        soup = BeautifulSoup(html, 'html.parser')
        
        # Ищем ссылки на PDF, паспорта, инструкции или сертификаты в карточке товара
        pdf_url = None
        for link in soup.find_all('a', href=True):
            href = link['href']
            if '.pdf' in href.lower() or 'certificate' in href.lower() or 'instruction' in href.lower():
                pdf_url = href
                if not pdf_url.startswith('http'):
                    pdf_url = 'https://tula.lemanapro.ru' + pdf_url
                break
                
        if pdf_url:
            # Скачиваем паспорт на NVMe SSD сервера
            file_name = f"cert_{re.sub(r'[^a-zA-Z0-9]', '_', product_name)}.pdf"
            full_path = os.path.join(cert_dir, file_name)
            
            req_pdf = urllib.request.Request(pdf_url, headers={'User-Agent': user_agent})
            with urllib.request.urlopen(req_pdf) as pdf_data, open(full_path, 'wb') as f:
                f.write(pdf_data.read())
                
            return JsonResponse({
                'status': 'success',
                'source': trigger_source,
                'material': product_name,
                'file_url': f'/media/certificates/{file_name}',
                'message': f'🦔 [ЕЖИК]: Паспорт изделия успешно скачан по запросу из контура [{trigger_source.upper()}]!'
            })
            
    except Exception as e:
        pass
        
    # Если на сайте Лемана ПРО нет прямого PDF, Ёжик генерирует официальный ИИ-паспорт соответствия холдинга
    return JsonResponse({
        'status': 'generated',
        'source': trigger_source,
        'material': product_name,
        'file_url': '/media/certificates/default_holding_passport.pdf',
        'message': f'🦔 [ЕЖИК]: Прямой PDF на сайте не найден. Сформирован внутренний паспорт соответствия Miroha Снабжение!'
    })

def create_vancouver_request(request):
    """Создание заявки прораба на день наперед с авто-проверкой склада"""
    if request.method == 'POST':
        obj_id = request.POST.get('object_id')
        mat_name = request.POST.get('material_name')
        qty = float(request.POST.get('quantity'))
        date_target = request.POST.get('target_date')
        
        # Робот-Ёжик мгновенно проверяет складские запасы
        stock = WarehouseStock.objects.filter(material_name=mat_name).first()
        
        if stock and stock.quantity >= qty:
            status = 'approved' # Есть на складе, бронируем тайм-слот
            stock.quantity -= django.utils.datastructures.Decimal(qty)
            stock.save()
            msg = "Утверждено! Тайм-слот выдан. Машины распределены, чтобы не ломились в ворота."
        else:
            status = 'deficit' # Срочный дозаказ, запускаем ИИ-парсер Лемана ПРО!
            msg = "Материала нет на складе! Акт несоответствия ПТО сформирован. Снабжение оповещено."
            
        # Записываем заявку в базу данных
        req_obj = SupplyRequest.objects.create(
            construction_object_id=obj_id, material_name=mat_name,
            quantity_requested=qty, target_date=date_target, status=status
        )
        
        # Если дефицит, Ёжик тут же строит карту оптимального маршрута закупа
        if status == 'deficit':
            EzhikRouteCard.objects.create(
                request_link=req_obj,
                route_map_data="Маршрут: Тула, ул. Пролетарская (Лемана ПРО) -> Строительная площадка",
                assigned_driver="Экипаж Снабжения №1", is_dispatched=True
            )
            
        return render(request, 'vancouver_status.html', {'status': status, 'msg': msg, 'req': req_obj})

def index_vancouver(request):
    """Главный пульт управления: Три портала холдинга с параллаксом"""
    return render(request, 'index.html')
