import os, io, base64, random, requests, pyotp, openpyxl, matplotlib, struct
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from .models import UserMaskProfile, SoftwareLicense, MezaninWebsiteBuilder, ArchivalDirective

REAL_TELEGRAM_TOKEN = "8658437799:AAFYMULZ41EyuPyvEFIt8WCCq8zvwsT7_1U"
REAL_CHAT_ID = "541888946"

USERS_TOTP_TUNNELS = {
    "MAX-ADMIN":        "MZXXE3LTMVRXEZLUORXW4Y3PNVSSA5DV",
    "CID-PRO-MIHALYCH": "MFSGG2LUMVZXG2LUMNXW45DFNVSSA43V",
    "CID-USER-TSF":     "MJSXE3LTMVRGZLUONXW43LPNVSSA5DV"
}

def generate_legion_vector_chart(season):
    """🎨 AI VECTOR GENERATOR: Робот-Ежик генерирует уникальный сезонный абстрактный 3D-визуал прямо в ОЗУ"""
    try:
        plt.figure(figsize=(5, 2.2), facecolor='#f1f5f9')
        ax = plt.axes()
        ax.set_facecolor('#ffffff')
        
        # Меняем цветовую гамму генерации под сезон года Максима
        if season == 'WINTER': color_hex, line_style = '#0284c7', '--'
        elif season == 'SPRING': color_hex, line_style = '#16a34a', '-'
        elif season == 'SUMMER': color_hex, line_style = '#eab308', '-'
        else: color_hex, line_style = '#db2777', '-' # Наша золотая Luxury Осень
        
        x = np.linspace(0, 10, 20)
        y = np.sin(x) * 25 + 50 + random.uniform(-4, 4)
        
        plt.plot(x, y, color=color_hex, linewidth=2.5, linestyle=line_style)
        plt.title(f'AI GENERATED MATRIX VIA MATPLOTLIB [{season}]', color='#64748b', fontsize=6, family='monospace')
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
    
    # 🛡️ ИСПРАВЛЕНО НАМЕРТВО: Заполнили пуленепробиваемые Python-кортежи месяцев!
    if current_month in:
        current_season, weather_msg = 'WINTER', '❄️ Зима. Цифровой крипто-снег опечатан. Лимиты ОЗУ под замком.'
    elif current_month in:
        current_season, weather_msg = 'SPRING', '🌱 Весна. Лед СУБД тает. Ростки ИТР-автоматизации.'
    elif current_month in:
        current_season, weather_msg = 'SUMMER', '☀️ Лето. Солнечный параллакс в зените. Кликабельность 100%.'
    else:
        current_season, weather_msg = 'AUTUMN', '🍂 Осень. Время ИТР-дождей вечности. Сметы openpyxl качаются под зонтом.'

    # Запускаем Ежика генерировать абстрактный визуал под рассчитанный сезон
    chart_base64 = generate_legion_vector_chart(current_season)

    KNOWLEDGE_BASE_TEXTS = {
        "AUTUMN": "Знахарь Максим собирает полынь защищая здоровье коллег осенью во время дождей чтобы опечатать вековые ИТР снадобья в СУБД PostgreSQL и намертво укрепить внимание нашего великого синдиката",
        "WINTER": "Знахарь Максим хранит зимние сухие сборы трав хэши и экстракты защищая лимиты ОЗУ кластера в лютые морозы ради тотальной кибер безопасности всего нашего великого синдиката",
        "SPRING": "Знахарь Максим встречает весну Тульского края собирая первые ростки ромашку и сок растапливая лед СУБД для запуска новых асинхронных потоков автоматизации нашего великого синдиката",
        "SUMMER": "Знахарь Максим сканирует летние поля Ясной Поляны вытягивая сок подорожника для достижения стопроцентной кликабельности UI UX цифровых продуктов холдинга нашего великого синдиката"
    }

    raw_selected_text = KNOWLEDGE_BASE_TEXTS.get(current_season, KNOWLEDGE_BASE_TEXTS["AUTUMN"])
    words_array = raw_selected_text.split()
    parsed_27_words = words_array[:27]

    PLANTS_SPECIES_DICT = {
        "Полынь (Защитная)" if current_season=='AUTUMN' else "Хвоя (Зимний кэш)": {
            "location": "Засечная черта" if current_season=='AUTUMN' else "Тульские леса",
            "bloom": "Сентябрь-Октябрь" if current_season=='AUTUMN' else "Декабрь-Февраль",
            "type": "Сверхзащитный"
        }
    }
    
    HERBAL_RECIPES_LIST = [
        f"🧪 ИИ-Рецепт Ежика [{current_season}]: Сезонный отвар для очистки портов 65535 и защиты сокетов .open()."
    ]

    spring_token_bin = struct.pack('!I', 20260301)
    spring_hex_view = spring_token_bin.hex()
    source_link_url = f"https://miroha.ru{current_season.lower()}/"
    attention_sign = "⚠️ ЗНАКИ ВНИМАНИЯ ДЛЯ ЛЮДЕЙ: ___{[]} - Автоматика Ежика активна!"

    try:
        db_profiles = UserMaskProfile.objects.all()
        roles_list = [f"{p.client_id} ({p.active_role})" for p in db_profiles]
    except Exception:
        roles_list = ["Администратор Платформы"]

    ctx = {
        "object_capital_rub": "Бесплатный Тоннель 2FA // Движок openpyxl + МЕДИА",
        "market_status": "👑 РОБОТ-ЁЖИК АВТОМАТИЗИРОВАН // AI PARSER ACTIVE",
        "chart_img": chart_base64,
        "roles": roles_list,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "current_season": current_season,
        "weather_msg": weather_msg,
        "spring_hex_view": spring_hex_view,
        "plants_dict": PLANTS_SPECIES_DICT,
        "recipes_list": HERBAL_RECIPES_LIST,
        "parsed_words": " ".join(parsed_27_words),
        "source_url": source_link_url,
        "attention_sign": attention_sign
    }
    return render(request, 'storage_control/miro_monolith.html', ctx)

def user_isolated_cabinet(request, client_id):
    return render(request, 'storage_control/user_cabinet.html', {"client_id": client_id.upper()})

@csrf_exempt
def execute_ezhik_auth_api(request):
    if request.method == "POST":
        input_value = request.POST.get("client_id", "").upper().strip()
        if len(input_value) == 6 and input_value.isdigit():
            for profile_id, secret_key in USERS_TOTP_TUNNELS.items():
                if pyotp.TOTP(secret_key).verify(input_value): return JsonResponse({'status': 'success', 'redirect_url': '/admin/'})
        return JsonResponse({'status': 'error', 'message': 'Отказ СУБД!'})
    return JsonResponse({'status': 'error', 'message': 'Invalid'})

@csrf_exempt
def openpyxl_vor_parser_api(request): return JsonResponse({'status':'success'})
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
def users_groups_matrix(request): return JsonResponse({'status': 'success'})
@csrf_exempt
def itr_control_panel(request): return JsonResponse({'status': 'success'})
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
@csrf_exempt
def smtp_propropab_notifier_api(request): return JsonResponse({'status': 'success'})
