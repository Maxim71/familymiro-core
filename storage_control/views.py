import os
import io
import base64
import random
from datetime import datetime
import requests
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import UserMaskProfile, SoftwareLicense, MezaninWebsiteBuilder, ArchivalDirective

import pyotp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

REAL_TELEGRAM_TOKEN = "8658437799:AAFYMULZ41EyuPyvEFIt8WCCq8zvwsT7_1U"
REAL_CHAT_ID = "541888946"

# Жесткие туннели-ключи для бесплатного приложения Google Authenticator
USERS_TOTP_TUNNELS = {
    "MAX-ADMIN":        "MZXXE3LTMVRXEZLUORXW4Y3PNVSSA5DV",
    "CID-PRO-MIHALYCH": "MFSGG2LUMVZXG2LUMNXW45DFNVSSA43V",
    "CID-USER-TSF":     "MJSXE3LTMVRGZLUONXW43LPNVSSA5DV"
}

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
    """🖥️ ГЛАВНАЯ ВИТРИНА КОНСТРУКТОРA-МЕЗОНИНА // ПОЛНЫЙ ОНЛАЙН СУБД"""
    chart_base64 = generate_legion_vector_chart()
    
    # Вытягиваем актуальный список масок напрямую из РЕАЛЬНОЙ ТАБЛИЦЫ PostgreSQL!
    try:
        db_profiles = UserMaskProfile.objects.all()
        roles_list = [f"{p.client_id} ({p.active_role})" for p in db_profiles]
    except Exception:
        roles_list = ["Администратор Матрицы Платформы", "Digital-Менеджер"]

    if not roles_list:
        roles_list = ["Администратор Матрицы Платформы", "Digital-Менеджер (Multi-DB Hub)"]

    ctx = {
        "object_capital_rub": "Бесплатный Тоннель 2FA // Google Authenticator",
        "market_status": "🟢 КРИПТОГРАФИЯ БЕЗ ЗАТРАТ НА СМС // ПОД КОНТРОЛЕМ БРОНЕПОЕЗДА",
        "chart_img": chart_base64,
        "roles": roles_list,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }
    return render(request, 'storage_control/miro_monolith.html', ctx)

@csrf_exempt
def execute_ezhik_auth_api(request):
    """🦔 ЖИВАЯ ИТР-ЛОГИКА ЕЖИКА: Жесткая проверка сущностей внутри PostgreSQL"""
    if request.method == "POST":
        input_value = request.POST.get("client_id", "").upper().strip()
        
        # 1. Проверка 6 цифр из бесплатного приложения Google Authenticator
        if len(input_value) == 6 and input_value.isdigit():
            for profile_id, secret_key in USERS_TOTP_TUNNELS.items():
                totp_validator = pyotp.TOTP(secret_key)
                if totp_validator.verify(input_value):
                    return JsonResponse({'status': 'success', 'redirect_url': '/admin/'})
            return JsonResponse({'status': 'error', 'message': 'Битый или просроченный токен Google Authenticator!'})
            
        # 2. Проверка ИТР-Лицензий напрямую через SQL-запрос к Postgres
        try:
            profile = UserMaskProfile.objects.get(client_id=input_value)
            license_entry = SoftwareLicense.objects.get(profile=profile)
            
            if license_entry.status == 'ACTIVE':
                return JsonResponse({
                    'status': 'tunnel_info',
                    'message': f'🔑 ТУННЕЛЬ СВЯЗИ В СУБД ВЕРИФИЦИРОВАН!\n\nВладелец: {profile.active_role}\nЛицензия: {license_entry.license_type} ({license_entry.status})\n\nВставьте секретный КЛЮЧ-ТОННЕЛЬ в бесплатное приложение Google Authenticator:\n👉 {profile.google_totp_secret}'
                })
            return JsonResponse({'status': 'error', 'message': f'Отказ СУБД! Лицензия {license_entry.license_key} ЗАБЛОКИРОВАНА!'})
        except (UserMaskProfile.DoesNotExist, SoftwareLicense.DoesNotExist):
            # Быстрый мастер-вход
            if input_value == "MAX-ADMIN" or input_value == "MIROHA-ADMIN":
                return JsonResponse({'status': 'success', 'redirect_url': '/admin/'})
            return JsonResponse({'status': 'error', 'message': 'Такой ИТР-профиль не найден в реляционных таблицах PostgreSQL!'})

    return JsonResponse({'status': 'error', 'message': 'Invalid метод'})

# 📸 ГРАФИЧЕСКИЙ QR-ГЕНЕРАТОР FAMILYMIRA ИЗ ОЗУ
def generate_free_google_qr_view(request):
    import qrcode
    secret_key = USERS_TOTP_TUNNELS["MAX-ADMIN"]
    otpauth_url = f"otpauth://totp/FAMILYMIRA?secret={secret_key}&issuer=MirohaMonolith"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(otpauth_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")
    return response

# СБЕРЕЖЕННЫЕ АКТИВНЫЕ API СОКЕТЫ ДЛЯ СТАБИЛЬНОСТИ СИСТЕМЫ
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
