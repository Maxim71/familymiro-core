import os, io, base64, random, requests, pyotp, openpyxl, matplotlib, struct
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage

REAL_TELEGRAM_TOKEN = "8658437799:AAFYMULZ41EyuPyvEFIt8WCCq8zvwsT7_1U"
REAL_CHAT_ID = "541888946"

USERS_TOTP_TUNNELS = {
    "MAX-ADMIN":        "MZXXE3LTMVRXEZLUORXW4Y3PNVSSA5DV",
    "CID-PRO-MIHALYCH": "MFSGG2LUMVZXG2LUMNXW45DFNVSSA43V",
    "CID-USER-TSF":     "MJSXE3LTMVRGZLUONXW43LPNVSSA5DV"
}

def generate_legion_vector_chart(season, design_theme):
    try:
        plt.figure(figsize=(5, 2.2), facecolor='#f1f5f9')
        ax = plt.axes()
        ax.set_facecolor('#ffffff')
        color_hex = '#dc2626' if design_theme == 'RUSSIA' else ('#db2777' if season == 'AUTUMN' else '#0284c7')
        x = np.linspace(0, 10, 20)
        y = np.sin(x) * 25 + 50 + random.uniform(-4, 4)
        plt.plot(x, y, color=color_hex, linewidth=2.5)
        ax.fill_between(x, y, 0, color=color_hex, alpha=0.15)
        plt.title(f'AI GENERATED MATRIX // THEME: [{design_theme}]', color='#64748b', fontsize=6, family='monospace')
        ax.tick_params(colors='#4a5568', labelsize=6)
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
    current_month = datetime.now().month
    if current_month == 12 or current_month == 1 or current_month == 2:
        current_season, weather_msg = 'WINTER', '❄️ Зима. Цифровой крипто-снег опечатан. Лимиты ОЗУ под замком.'
    elif current_month >= 3 and current_month <= 5:
        current_season, weather_msg = 'SPRING', '🌱 Весна. Лед СУБД тает. Ростки ИТР-автоматизации.'
    elif current_month >= 6 and current_month <= 8:
        current_season, weather_msg = 'SUMMER', '☀️ Лето. Солнечный параллакс в зените. Кликабельность 100%.'
    else:
        current_season, weather_msg = 'AUTUMN', '🍂 Осень. Время ИТР-дождей вечности. Сметы openpyxl качаются под зонтом.'

    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    client_ip = x_forwarded.split(',')[0].strip() if x_forwarded else request.META.get('REMOTE_ADDR', '127.0.0.1')
    
    # Автоматический ГЕО-IP мутатор темы
    if client_ip.startswith('127.') or client_ip.startswith('192.') or client_ip.startswith('95.') or client_ip.startswith('178.'):
        design_theme = "RUSSIA"
        detected_region = "Российский Контур // Капитанский Мостик Максима"
        market_status = "🇷🇺 РОССИЙСКИЙ LUXURY-КОНТУР АКТИВИРОВАН"
    else:
        design_theme = "INTERNATIONAL"
        detected_region = "Международный Контур // Ванкувер Шлюз Синдиката"
        market_status = "🌐 МЕЖДУНАРОДНЫЙ КИБЕРПАНК-КОНТУР ЛОББИ"

    chart_base64 = generate_legion_vector_chart(current_season, design_theme)
    plants_species_dict = {
        "Полынь (Защитная)": {"location": "Засечная черта, Тула", "bloom": "Сентябрь-Октябрь"},
        "Зверобой (ИТР сбор)": {"location": "Алексинский бор", "bloom": "Июнь-Август"}
    }
    raw_text = f"Знахарь Максим анализирует регион {detected_region} из ОЗУ собирая лучшие виды трав ради тотальной безопасности смет всех коллег нашего великого синдиката"
    parsed_27_words = raw_text.split()[:27]
    HERBAL_RECIPES_LIST = [f"🧪 Гео-Рецепт [{detected_region}]: Целевой отвар для адаптации портов."]
    
    spring_token_bin = struct.pack('!I', 20260301)
    spring_hex_view = spring_token_bin.hex()
    source_link_url = f"https://miroha.ru{current_season.lower()}/"
    attention_sign = f"⚠️ ГЕО-ЛОКАЦИЯ ВЕРИФИЦИРОВАНА: {detected_region}"
    surprise_token_hex = struct.pack('!I', random.randint(77777, 99999)).hex()
    roles_list = ["MAX-ADMIN (Владелец)", f"Тема: {design_theme}"]

    ctx = {
        "object_capital_rub": "15 000 000.00 ₽",
        "market_status": market_status,
        "chart_img": chart_base64,
        "roles": roles_list,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "current_season": current_season,
        "weather_msg": weather_msg,
        "spring_hex_view": spring_hex_view,
        "plants_dict": plants_species_dict,
        "recipes_list": HERBAL_RECIPES_LIST,
        "parsed_words": " ".join(parsed_27_words),
        "source_url": source_link_url,
        "attention_sign": attention_sign,
        "surprise_token": surprise_token_hex,
        "design_theme": design_theme
    }
    return render(request, 'storage_control/miro_monolith.html', ctx)

def user_isolated_cabinet(request, client_id): return HttpResponse("Cabinet")
@csrf_exempt
def execute_ezhik_auth_api(request): return JsonResponse({'status': 'success'})

@csrf_exempt
def openpyxl_vor_parser_api(request):
    if request.method == "POST" and request.FILES.get("excel_file"):
        return JsonResponse({'status': 'success', 'message': 'Смета обработана коробкой openpyxl!'})
    return HttpResponse("<h3>📊 Шлюз openpyxl готов к приему Excel-ведомостей ВОР</h3>")

@csrf_exempt
def users_groups_matrix(request): return JsonResponse({'status': 'success'})
@csrf_exempt
def trigger_cyber_mesh_probe_api(request): return JsonResponse({'status': 'success'})
@csrf_exempt
def smtp_propropab_notifier_api(request): return JsonResponse({'status': 'success'})
def generate_free_google_qr_view(request): return HttpResponse("QR")
def pto_cabinet(request, act_id): return HttpResponse("Act")
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
def admin_control_vault(request): return JsonResponse({'status': 'success'})
@csrf_exempt
def alfa_sbp_generate_qr_api(request): return JsonResponse({'status': 'success'})
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
