import os
import io
import base64
import random
from datetime import datetime
import requests
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

import pyotp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Вечные Base32 секреты-туннели для бесплатного приложения Google Authenticator в СУБД
USERS_TOTP_TUNNELS = {
    "MAX-ADMIN":        "MZXXE3LTMVRXEZLUORXW4Y3PNVSSA5DV",
    "CID-PRO-MIHALYCH": "MFSGG2LUMVZXG2LUMNXW45DFNVSSA43V",
    "CID-USER-TSF":     "MJSXE3LTMVRGZLUONXW43LPNVSSA5DV"
}

MAXIM_ROLES_REGISTRY = [
    "Администратор Матрицы Платформы", "Digital-Менеджер (Multi-DB Hub)", "Пользователь", 
    "Разнорабочий", "ПТО", "Менеджер проекта", "Отец для вечности", "Блогер (видеомонтаж)", 
    "Менеджер digital", "SEO-оптимизатор", "Менеджер-продажник", "Снабженец", "Начальник участка", 
    "Обычный юзер", "Китаец (COSCO)", "КНДР-партнер", "Русский мастер", "Ребенок", "Аналитик и архитектор Ёжика и Жука"
]

def generate_legion_vector_chart():
    try:
        plt.figure(figsize=(5, 2.2), facecolor='#f1f5f9')
        ax = plt.axes()
        ax.set_facecolor('#ffffff')
        x = np.linspace(0, 10, 15)
        y = np.sin(x) * 30 + 40 + random.uniform(-2, 2)
        plt.plot(x, y, color='#db2777', linewidth=2)
        plt.title('БЕСПЛАТНЫЙ КРИПТО-ТУННЕЛЬ: СВЕРКА ТОКЕНОВ ВРЕМЕНИ GOOGLE 2FA', color='#64748b', fontsize=7, family='monospace')
        ax.tick_params(colors='#4a5568', labelsize=6)
        ax.spines['bottom'].set_color('#cbd5e1')
        ax.spines['left'].set_color('#cbd5e1')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.grid(True, color='#e2e8f0', linestyle='--', linewidth=0.5)
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=130, facecolor='#f1f5f9')
        buf.seek(0)
        string = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        return f"data:image/png;base64,{string}"
    except Exception: return ""

def index_vancouver(request):
    chart_base64 = generate_legion_vector_chart()
    print("=============================================================")
    print("🛰️  [БЕСПЛАТНЫЙ DevOps ТУННЕЛЬ С ТЕЛЕФОНОМ // ТЕКУЩИЕ КОДЫ]:")
    print(f"🔑 Для логина MAX-ADMIN код прямо сейчас: {pyotp.TOTP(USERS_TOTP_TUNNELS['MAX-ADMIN']).now()}")
    print(f"👷 Для CID-PRO-MIHALYCH код прямо сейчас: {pyotp.TOTP(USERS_TOTP_TUNNELS['CID-PRO-MIHALYCH']).now()}")
    print("=============================================================")
    ctx = {
        "object_capital_rub": "Бесплатный Тоннель 2FA // Google Authenticator",
        "market_status": "🟢 КРИПТОГРАФИЯ БЕЗ ЗАТРАТ НА СМС // ПОД КОНТРОЛЕМ БРОНЕПОЕЗДА",
        "chart_img": chart_base64,
        "roles": MAXIM_ROLES_REGISTRY,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }
    return render(request, 'storage_control/miro_monolith.html', ctx)

@csrf_exempt
def execute_ezhik_auth_api(request):
    if request.method == "POST":
        input_value = request.POST.get("client_id", "").upper().strip()
        if len(input_value) == 6 and input_value.isdigit():
            for profile_id, secret_key in USERS_TOTP_TUNNELS.items():
                totp_validator = pyotp.TOTP(secret_key)
                if totp_validator.verify(input_value):
                    return JsonResponse({'status': 'success', 'redirect_url': '/admin/'})
            return JsonResponse({'status': 'error', 'message': 'Битый или просроченный токен Google Authenticator! Код живет ровно 30 секунд.'})
        target_tunnel = USERS_TOTP_TUNNELS.get(input_value)
        if target_tunnel:
            return JsonResponse({
                'status': 'tunnel_info',
                'message': f'🔑 ТУННЕЛЬ СВЯЗИ В СУБД НАЙДЕН!\nВставьте секретный КЛЮЧ-ТОННЕЛЬ в бесплатное приложение Google Authenticator:\n👉 {target_tunnel}'
            })
        return JsonResponse({'status': 'error', 'message': 'Введенный ИТР-код или токен 2FA не найден в реестре PostgreSQL!'})
    return JsonResponse({'status': 'error', 'message': 'Invalid method'})

def user_isolated_cabinet(request, client_id): return render(request, 'storage_control/user_cabinet.html')
def pto_cabinet(request, act_id): return HttpResponse("Act Cabinet")
def neuro_radar_dashboard(request): return HttpResponse("Radar")
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
def add_to_cart_api(request, product_id): return JsonResponse({'status': 'success'})
@csrf_exempt
def checkout_sbp_payment_api(request): return JsonResponse({'status': 'success'})
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
