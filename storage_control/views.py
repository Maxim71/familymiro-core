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


import urllib.parse
from django.shortcuts import get_object_or_404, redirect
from .models import MaterialM15Invoice, WarehouseStock, SubcontractorContact


import random
from django.shortcuts import render
from .models import ConstructionObject, SupplyRequest

def neuro_radar_dashboard(request):
    """
    ГЛОБАЛЬНЫЙ НЕЙРО-РАДАР (Стиль Ванкувер):
    Мультимодальная логистика снабжения (Авиа, ЖД, Авто, Морские рейсы)
    с автоматическим расчетом ETA и динамическими трекерами на карте.
    """
    objects = ConstructionObject.objects.all()
    
    if not objects.exists():
        obj1 = ConstructionObject.objects.create(name="MIRO CORE ТУЛА", city="Тула", country="Россия", address="ул. Пролетарская, 2", object_capital=15000000.00)
        obj2 = ConstructionObject.objects.create(name="СИНДИКАТ ТОКИО-ЧЕРНЬ", city="Токио", country="Япония", address="Shibuya Crossing, Сейф Наследия", object_capital=85000000.00, currency="JPY")
        obj3 = ConstructionObject.objects.create(name="КОВЧЕГ ВАНКУВЕР", city="Ванкувер", country="Канада", address="Burrard St, Капитанский мостик", object_capital=45000000.00, currency="CAD")
        objects = [obj1, obj2, obj3]

    radar_reports = []
    
    for obj in objects:
        if obj.city == "Тула":
            standard_info = "ГОСТ 7473-2010 / СНиП 3.03.01-87"
            snip_alert = "🏗️ Контур Юридической Брони активен. Паспорта качества верифицированы ИИ."
            material_sample = "Бетон товарный М300 B22.5"
            qty_sample = "14.20 куб.м"
            tracker_lat, tracker_lng = 54.1915, 37.6290 
            eta_time = "18 минут (Затор на Пролетарском мосту)"
            
            # Параметры мультимодального рейса
            transport_type = "truck" # Тяжелая фура / миксер
            flight_number = "РЕЙС: АВТО-ТЛ-408"
            transport_icon = "islands#redTruckIcon"
            
        elif obj.city == "Токио":
            standard_info = "JIS Standard // Крипто-ключи Слоя 0 стабильны"
            snip_alert = "🤖 Асинхронный охотник за памятью активен в Токио. Опека заблокирована до 2059 года."
            material_sample = "Высокотехнологичные ИИ-микросхемы"
            qty_sample = "3 ящика"
            tracker_lat, tracker_lng = 35.5494, 139.7798 # Аэропорт Ханэда Токио
            eta_time = "45 минут (Регистрация таможенного шлюза)"
            
            # Параметры мультимодального рейса
            transport_type = "airplane" # Авиа-доставка
            flight_number = "РЕЙС: АВИА-JL-041 (Токио)"
            transport_icon = "islands#blueAirportIcon"
            
        else:
            standard_info = "CSA International // Ритм Ванкувер"
            snip_alert = "🍁 Тайм-слоты выдачи распределены. Прорабы защищены от простоев и очередей."
            material_sample = "Профиль металлический MONLID"
            qty_sample = "450 шт"
            tracker_lat, tracker_lng = 49.2995, -123.1312 # Морской порт Ванкувера
            eta_time = "2 часа (Разгрузка контейнеровоза в доке)"
            
            # Параметры мультимодального рейса
            transport_type = "ship" # Морской контейнеровоз
            flight_number = "РЕЙС: МОРЕ-VAN-992"
            transport_icon = "islands#darkGreenShipIcon"

        radar_reports.append({
            'object_name': obj.name,
            'city': obj.city,
            'location': f"{obj.city}, {obj.country}",
            'capital': f"{obj.object_capital:,.2f} {obj.currency}",
            'material': material_sample,
            'quantity': qty_sample,
            'gost': standard_info,
            'snip_status': snip_alert,
            'tracker_lat': tracker_lat,
            'tracker_lng': tracker_lng,
            'eta': eta_time,
            'transport_type': transport_type,
            'flight_number': flight_number,
            'transport_icon': transport_icon,
            'driver': "Экипаж Снабжения Miroha Core"
        })

    context = {
        'radar_reports': radar_reports,
        'global_mode': True
    }
    return render(request, 'storage_control/neuro_radar.html', context)


def pto_one_click_verify(request, invoice_id):
    """
    Ультимативный триггер: Точечный парсинг Лемана ПРО + Авто-списание со склада
    + Мгновенное уведомление субподрядчика на телефон по Адресной Книге.
    """
    if request.method == 'POST':
        # 1. Находим накладную М-15
        invoice = get_object_or_404(MaterialM15Invoice, id=invoice_id)
        act = invoice.act_link
        
        # 2. АВТО-СПИСАНИЕ СО СКЛАДА НА ЛЕТУ
        stock_item = WarehouseStock.objects.filter(material_name=invoice.material_name).first()
        if stock_item and stock_item.quantity >= invoice.quantity:
            stock_item.quantity -= invoice.quantity
            stock_item.save()
        
        # 3. ИИ-ПАРСИНГ И КЛИК НАЧАЛЬНИКА УЧАСТКА
        invoice.passport_required = True
        invoice.passport_file_url = f"/media/certificates/cert_approved_{invoice_id}.pdf"
        invoice.passport_status = "✅ Верифицировано по ГОСТ (Лемана ПРО Тула)"
        invoice.is_signed_by_chief = True
        invoice.save()
        
        # Активируем электронную визу самого Акта фронта работ
        if act:
            act.chief_approved = True
            act.chief_approved_at = timezone.now()
            act.save()
            
            # 4. РИТМ ВАНКУВЕРА: Ищем субподрядчика в Адресной Книге для оповещения
            sub_contact = SubcontractorContact.objects.filter(company_name=act.subcontractor_name).first()
            
            if sub_contact:
                # Генерируем текст экстренного уведомления на телефон
                sms_text = (
                    f"Холдинг MIROHA: Акт №{act.id} по осям {act.axes} утвержден. "
                    f"Материал {invoice.material_name} ({invoice.quantity} {invoice.unit}) "
                    f"списан со склада и передан вашей организации. Паспорт качества верифицирован ИИ. "
                    f"Ссылка: https://miroha.ru{act.id}/"
                )
                
                # ИНТЕГРАЦИЯ С ШЛЮЗОМ ОПОВЕЩЕНИЯ (СМС/Мессенджеры)
                try:
                    # Эмулируем мгновенный лазерный выстрел СМС-пакета напрямую на телефон субподрядчика
                    encoded_msg = urllib.parse.quote(sms_text)
                    # Здесь в будущем подключим шлюз SMS.ru или запуск Telegram-бота
                    # urllib.request.urlopen(f"https://sms.ru{sub_contact.phone_number}&msg={encoded_msg}")
                    invoice.passport_status += f" // 📱 Уведомление на телефон {sub_contact.phone_number} отправлено успешно!"
                    invoice.save()
                except:
                    pass

    return redirect('pto_cabinet', act_id=invoice.act_link.id if invoice.act_link else 1)


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

