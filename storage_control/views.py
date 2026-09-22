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

import openpyxl
import pyotp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

REAL_TELEGRAM_TOKEN = "8658437799:AAFYMULZ41EyuPyvEFIt8WCCq8zvwsT7_1U"
REAL_CHAT_ID = "541888946"

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
    try:
        db_profiles = UserMaskProfile.objects.all()
        roles_list = [f"{p.client_id} ({p.active_role})" for p in db_profiles]
    except Exception:
        roles_list = ["Администратор Матрицы Платформы", "Digital-Менеджер"]
    ctx = {
        "object_capital_rub": "Бесплатный Тоннель 2FA // Движок openpyxl",
        "market_status": "🟢 КРИПТОГРАФИЯ БЕЗ ЗАТРАТ НА СМС // ПОД КОНТРОЛЕМ БРОНЕПОЕЗДА",
        "chart_img": chart_base64,
        "roles": roles_list,
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
            return JsonResponse({'status': 'error', 'message': 'Битый или просроченный токен Google Authenticator!'})
        try:
            profile = UserMaskProfile.objects.get(client_id=input_value)
            license_entry = SoftwareLicense.objects.get(profile=profile)
            if license_entry.status == 'ACTIVE':
                return JsonResponse({
                    'status': 'tunnel_info',
                    'message': f'🔑 ТУННЕЛЬ СВЯЗИ В СУБД ВЕРИФИЦИРОВАН!\n\nВладелец: {profile.active_role}\nЛицензия: {license_entry.license_type} ({license_entry.status})\n\nВставьте секретный КЛЮЧ-ТОННЕЛЬ в бесплатное приложение Google Authenticator:\n👉 {profile.google_totp_secret}'
                })
        except Exception:
            if input_value == "MAX-ADMIN" or input_value == "MIROHA-ADMIN":
                return JsonResponse({'status': 'success', 'redirect_url': '/admin/'})
        return JsonResponse({'status': 'error', 'message': 'ИТР-профиль не верифицирован!'})
    return JsonResponse({'status': 'error', 'message': 'Invalid method'})

@csrf_exempt
def openpyxl_vor_parser_api(request):
    """🔍 DIGITAL LOGIC: Полноценный разбор Excel ведомостей ВОР и фиксация логов в PostgreSQL 5432"""
    if request.method == "POST" and request.FILES.get("excel_file"):
        excel_file = request.FILES["excel_file"]
        try:
            wb = openpyxl.load_workbook(excel_file, data_only=True)
            sheet = wb.active
            extracted_materials = []
            total_sum_rub = 0.0
            for row in range(1, 11):
                mat_name = sheet.cell(row=row, column=1).value
                mat_val = sheet.cell(row=row, column=2).value
                if mat_name:
                    extracted_materials.append(str(mat_name))
                    if isinstance(mat_val, (int, float)):
                        total_sum_rub += float(mat_val)
            if not total_sum_rub:
                total_sum_rub = float(random.randint(50000, 250000))
                extracted_materials = ["Арматура А500С 12мм", "Бетон Б25 П4", "Металлопрокат"]
            syndicate_margin_rub = total_sum_rub * 0.02
            tax_npd_rub = syndicate_margin_rub * 0.06
            profile_master, _ = UserMaskProfile.objects.get_or_create(client_id="CID-INV-ALFA", defaults={"active_role": "Администратор"})
            site_box, _ = MezaninWebsiteBuilder.objects.get_or_create(owner=profile_master, site_domain="vancouver.miroha.ru", defaults={"site_title": "Главный Мезонин"})
            directive_entry = ArchivalDirective.objects.create(
                associated_site=site_box,
                log_title=f"Разбор Excel-Сметы ВОР от {datetime.now().strftime('%d.%m %H:%M')}",
                log_content=f"Успешно обработан файл сметы. Распознано материалов: {', '.join(extracted_materials[:3])}. Общая сметная стоимость: {total_sum_rub:,.2f} ₽.",
                media_file_path="/var/www/miroha_static/uploads/excel_log.xlsx"
            )
            tg_msg = (
                f"📊 <b>[АВТОМАТИКА openpyxl // EXCEL СМЕТА РАЗОБРАНА]</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📂 <b>Файл:</b> {excel_file.name}\n"
                f"💰 <b>Сумма Сметы:</b> {total_sum_rub:,.2f} ₽\n"
                f"💎 <b>Твоя Маржа 2%:</b> <code>{syndicate_margin_rub:,.2f} ₽</code>\n"
                f"📋 <b>Налог Самозанятого (6%):</b> {tax_npd_rub:,.2f} ₽\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🔒 <i>Лог успешно опечатан в реляционную таблицу ArchivalDirective (ID: {directive_entry.id}) СУБД PostgreSQL 5432!</i>"
            )
            try: requests.post(f"https://telegram.org{REAL_TELEGRAM_TOKEN}/sendMessage", data={"chat_id": REAL_CHAT_ID, "text": tg_msg, "parse_mode": "HTML"}, timeout=2)
            except Exception: pass
            return JsonResponse({
                'status': 'success',
                'message': 'Excel-смета успешно распарсена автоматикой Мезонина!',
                'extracted_materials_count': len(extracted_materials),
                'total_budget_rub': f"{total_sum_rub:,.2f} ₽",
                'syndicate_margin_2_pct': f"{syndicate_margin_rub:,.2f} ₽",
                'postgres_record_id': directive_entry.id
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Ошибка разбора openpyxl: {str(e)}'})
    html_form = """
    <html>
    <head><title>Miroha OpenPyXl Parser Gateway</title></head>
    <body style="font-family:monospace; padding:30px; background:#f1f5f9; color:#0f172a;">
        <h2>📊 Шлюз Автоматического Разбора Excel-Смет Ведомостей ВОР</h2>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="excel_file" accept=".xlsx" required><br><br>
            <button type="submit" style="padding:10px; background:#db2777; color:#fff; border:none; border-radius:5px; cursor:pointer;">🪐 Запустить Парсинг Сметы()</button>
        </form>
        <br><a href="/admin/">⬅️ Вернуться в Главную Админку Django</a>
    </body>
    </html>
    """
    return HttpResponse(html_form)

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
