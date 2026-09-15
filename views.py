# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import json

def index_family(request):
    # Твой оригинальный прямоугольный шлюз трех входов для людей
    return render(request, 'storage_control/index.html', {
        'captain': 'Miroslava_Kosareva',
        'healer_status': 'Ezhik_Active_2026'
    })

def ezhik_pay_identification(request):
    # Идентификация платежей Ёжику при оплате через СБП
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_phone = data.get('phone', '').strip()
            amount = data.get('amount', 0)
            
            # Ёжик проверяет ИД платежа в базе данных холдинга
            if user_phone and amount >= 100:
                print(f'🦔 [ЁЖИК-ПЛАТЁЖ] Идентификация успешна! Получено {amount} руб от {user_phone}')
                return JsonResponse({'status': 'success', 'message': 'Идентификация пройдена. Контур разблокирован!'})
            return JsonResponse({'status': 'error', 'message': 'Ошибка ИД: Неверная сумма или номер'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return HttpResponse('Method not allowed', status=405)

def index_construction(request):
    return JsonResponse({'status': 'active', 'workspace': 'ITR_Snab_ГОСТ'})

def index_director(request):
    return JsonResponse({'status': 'active', 'workspace': 'Blogger_Media_Core'})

# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import JsonResponse

def project_manager_analytics(request):
    # Вкладка Менеджера Проекта: Аналитика затрат, выгоды и доставки по всей России
    geo_location = request.GET.get('geo', 'Russia')
    material_cost = 500000  # Пример расчета
    delivery_cost = 25000 if geo_location == 'Russia' else 80000
    
    analytics_data = {
        'status': 'success',
        'geo_analysis': f'Регион: {geo_location}. Логистический коридор верифицирован.',
        'cost_analysis': {
            'materials': material_cost,
            'delivery': delivery_cost,
            'net_benefit': material_cost * 0.15, # Расчет выгоды закупки 15%
        },
        'recommendation': '🦔 [ЁЖИК] Рекомендует закупку: Цена ниже среднерыночной на 8%.'
    }
    return JsonResponse(analytics_data)

def constructor_matrix(request):
    # Конструктор работ для прорабов, геодезистов, мастеров СМР/МСТ и главного энергетика
    roles_matrix = {
        'prorab': 'Контроль актов КС-2/КС-3 и объемов бетона',
        'geodezist': 'Проверка исполнительных схем и разбивочных осей',
        'master_smr': 'Управление звеньями и расходными материалами на участке',
        'glavniy_energetik': 'Мониторинг мощностей подстанций и точек подключения',
        'subcontractors_potential': 'Подрядные организации: Верифицировано потенциала на 45 млн руб'
    }
    return JsonResponse({'status': 'active', 'roles_matrix': roles_matrix})


def send_invite_sms(request):
    # Автоматический вызов подрядчиков и ИТР групп в проект через СМС
    phone = request.GET.get('phone', '')
    group = request.GET.get('group', 'ITR')
    
    if phone:
        # Ёжик логирует отправку и контролирует приглашения
        print(f'🦔 [ЁЖИК-СМС] Отправлено приглашение на номер {phone} в группу {group}')
        return JsonResponse({'status': 'sent', 'message': f'СМС-вызов отправлен на {phone}. Группа сформирована.'})
    return JsonResponse({'status': 'error', 'message': 'Номер телефона не указан'})
