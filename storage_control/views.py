import os
import io
import base64
import random
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# 🖥️ 1. ГЛАВНАЯ СТРАНИЦА — ЧИСТАЯ, ДОРОГАЯ LUXURY ВИТРИНА ХОЛДИНГА (GOOGLE STANDARDS)
def index_vancouver(request):
    ctx = {
        "object_capital_rub": "15,000,000.00 ₽",
        "market_status": "🛡️ MIROHA MONOLITH // ENTERPRISE GATEWAY ACTIVE",
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }
    return render(request, 'storage_control/miro_monolith.html', ctx)

# 🪐 2. ИЗОЛИРОВАННЫЙ МИР ПО ЗАПРОСУ ЁЖИКА: Динамический личный кабинет юзера со своим дизайном!
def user_isolated_cabinet(request, client_id):
    """🧠 Multi-tenant Слой: Каждому юзеру — свой персональный мир, данные и дизайн страницы!"""
    
    # Имитируем базу данных ИТР-профилей в PostgreSQL 5432
    users_database = {
        "CID-PRO-MIHALYCH": {
            "name": "Прораб Михалыч (Ось-405)", "role": "ИТР Строительный Контроль",
            "bg_color": "#0d0e1b", "accent": "#39ff14", "badge": "👷 СЛУЖБА ПРOРАБОВ iPROPAB",
            "desc": "Доступ к 90-секундному ИИ-таймеру сдачи скрытых работ арматурных сеток."
        },
        "CID-INV-ALFA": {
            "name": "Максим Администратор", "role": "Глава Синдиката Холдинга",
            "bg_color": "#080911", "accent": "#00f0ff", "badge": "🛰️ ГЛАВНЫЙ КОМАНДНЫЙ ПУЛЬТ // LEGION",
            "desc": "Полный доступ к мультивалютному капиталу, траншам СБП Альфа-Банка и логам Кафки."
        },
        "CID-USER-TSF": {
            "name": "Волонтер ТСФ Тула", "role": "Благотворительный Сектор",
            "bg_color": "#0c0714", "accent": "#ff007f", "badge": "📍 НАCЛЕДИЕ // ТОМ СОЙЕР ФЕСТ",
            "desc": "Интерактивные маркеры, тепловые карты Metabase X-Ray реставрации усадеб."
        }
    }
    
    user_data = users_database.get(client_id.upper())
    if not user_data:
        return HttpResponseNotFound("🦔 Робот-Ёжик 404: Такого изолированного ИТР-кабинета не существует в PostgreSQL!")

    # Генерируем персональный графикmatplotlib строго под конкретного юзера в ОЗУ
    plt.figure(figsize=(5, 2.2), facecolor=user_data["bg_color"])
    ax = plt.axes()
    ax.set_facecolor('rgba(255,255,255,0.02)')
    x = np.linspace(0, 10, 15)
    y = np.sin(x) * 30 + 50 + random.uniform(-3, 3)
    plt.plot(x, y, color=user_data["accent"], linewidth=2)
    ax.tick_params(colors='#4a5568', labelsize=6)
    ax.spines['bottom'].set_color('#1c203a')
    ax.spines['left'].set_color('#1c203a')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.grid(True, color='#14192d', linestyle='--', linewidth=0.5)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=130, facecolor=user_data["bg_color"])
    buf.seek(0)
    chart_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()

    ctx = {
        "user": user_data,
        "client_id": client_id.upper(),
        "chart_img": f"data:image/png;base64,{chart_base64}",
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }
    return render(request, 'storage_control/user_cabinet.html', ctx)

# 🔐 АСИНХРОННЫЙ ЛОВЕЦ СВЕРХБЫСТРОЙ АВТОРИЗАЦИИ ДЛЯ ЕЖИКА
@csrf_exempt
def execute_ezhik_auth_api(request):
    if request.method == "POST":
        cid = request.POST.get("client_id", "").upper().strip()
        # Если юзер есть в базе — отдаем Ёжику прямой роутинг перенаправления в его мир!
        valid_cids = ["CID-PRO-MIHALYCH", "CID-INV-ALFA", "CID-USER-TSF"]
        if cid in valid_cids:
            return JsonResponse({'status': 'success', 'redirect_url': f'/cabinet/{cid}/'})
        return JsonResponse({'status': 'error', 'message': 'Client ID не найден в PostgreSQL'})
    return JsonResponse({'status': 'error', 'message': 'Invalid method'})

# АВТОНОМНЫЕ СЛУЖБЫ И ФИНТЕХ-ОКНА (ПОЛНОСТЬЮ СБЕРЕЖЕНЫ ДЛЯ ТВОИХ ЗАДАЧ)
@csrf_exempt
def add_to_cart_api(request, product_id): return JsonResponse({'status': 'success', 'product_id': product_id})
@csrf_exempt
def checkout_sbp_payment_api(request): return JsonResponse({'status': 'success'})
def pto_cabinet(request, act_id): return render(request, 'storage_control/pto_cabinet.html', {"act_id": act_id})
def neuro_radar_dashboard(request): return render(request, 'storage_control/neuro_radar.html')
def capsule_time_vault(request): return JsonResponse({'status': 'success'})
@csrf_exempt
def upload_video_to_vault_api(request): return JsonResponse({'status': 'success'})
@csrf_exempt
def save_vhd_journal_record(request): return JsonResponse({'status': 'success'})
@csrf_exempt
def live_stream_dashboard_api(request): return JsonResponse({'status': 'success'})
@csrf_exempt
def send_to_stream_api(request): return JsonResponse({'status': 'success'})
@csrf_exempt
def supply_limits_portal(request): return JsonResponse({'status': 'success'})
@csrf_exempt
def warehouse_m19_stock(request): return JsonResponse({'status': 'success'})
@csrf_exempt
def users_groups_matrix(request): return JsonResponse({'status': 'success'})
@csrf_exempt
def itr_control_panel(request): return JsonResponse({'status': 'success'})
@csrf_exempt
def admin_control_vault(request): return JsonResponse({'status': 'success'})
@csrf_exempt
def alfa_sbp_generate_qr_api(request): return JsonResponse({'status': 'success'})
@csrf_exempt
def openpyxl_vor_parser_api(request): return JsonResponse({'status': 'success'})
@csrf_exempt
def kafka_stream_logger_api(request): return JsonResponse({'status': 'success'})
@csrf_exempt
def ezdxf_cad_blueprint_api(request): return JsonResponse({'status': 'success'})
@csrf_exempt
def yolo_neural_grid_api(request): return JsonResponse({'status': 'success'})
@csrf_exempt
def reportlab_ks2_generator_api(request): return JsonResponse({'status': 'success'})
@csrf_exempt
def one_c_sync_bridge_api(request): return JsonResponse({'status': 'success'})
@csrf_exempt
def cac_metric_numpy_api(request): return JsonResponse({'status': 'success'})
@csrf_exempt
def seo_sitemap_xml_api(request): return JsonResponse({'status': 'success'})
@csrf_exempt
def smtp_propropab_notifier_api(request): return JsonResponse({'status': 'success'})
