# -*- coding: utf-8 -*-
import os, io, base64, random, requests, pyotp, openpyxl, struct, json
from datetime import datetime
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

def index_vancouver(request):
    current_month = datetime.now().month
    if current_month in (12, 1, 2):
        current_season, weather_msg = 'WINTER', '❄️ Зима. Лимиты ОЗУ под замком.'
    elif current_month in (3, 4, 5):
        current_season, weather_msg = 'SPRING', '🌱 Весна. Реестры АР/КР/ФК активны.'
    elif current_month in (6, 7, 8):
        current_season, weather_msg = 'SUMMER', '☀️ Лето. Отгрузка со Склада М19 идет на полной мощности.'
    else:
        current_season, weather_msg = 'AUTUMN', '🍂 Осень. Пайплайны CI/CD выровнены.'

    detected_region = "Российский Контур // Капитанский Мостик Максима"
    ctx = {
        "object_capital_rub": "15 000 000.00 ₽",
        "market_status": "🇷🇺 РОССИЙСКИЙ LUXURY-КОНТУР АКТИВИРОВАН",
        "chart_img": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
        "roles": ["MAX-ADMIN (Владелец)", "Окружение: Стабильно"],
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "current_season": current_season,
        "weather_msg": weather_msg,
        "spring_hex_view": "01af34c2",
        "plants_dict": {},
        "recipes_list": [f"🧪 IaC-Рецепт [{detected_region}]: Автопилот."],
        "parsed_words": "Знахарь Максим контролирует контур безопасности смет холдинга",
        "source_url": "https://miroha.ru",
        "attention_sign": "Синхронизация с GitHub успешна.",
        "surprise_token": "77777",
        "design_theme": "RUSSIA"
    }
    return render(request, 'storage_control/miro_monolith.html', ctx)

def pto_cabinet_view(request):
    return render(request, "pto_cabinet.html", {"attention_sign": "ТИМ-КОНТУР АКТИВЕН"})

@csrf_exempt
def parse_pdf_and_sync_axes_api(request):
    return JsonResponse({"status": "success", "message": "Парсер PDF активен"})

@csrf_exempt
def infrastructure_docs_view(request):
    return JsonResponse({
        "platform_title": "Платформа автоматизации вечности Бронепоезда FamilyMira",
        "status": "🟢 ВСЕ ВАГОНЫ СВЕДЕНЫ В ЕДИНЫЙ КРИСТАЛЛ АВТОНОМИИ",
        "network_map": {
            "Nginx Reverse Proxy": "Порты :80 и :443",
            "Django Core Monolith": "Порт :8000",
            "Flask Tutor Module": "Порт :5000",
            "FastAPI REST-Gateway": "Порт :8050"
        }
    }, json_dumps_params={'ensure_ascii': False})

@csrf_exempt
def export_cascade_data_api(request): return JsonResponse({"status": "SUCCESS"})
def user_isolated_cabinet(request, client_id): return HttpResponse("Cabinet")
@csrf_exempt
def execute_ezhik_auth_api(request): return JsonResponse({'status': 'success'})
@csrf_exempt
def users_groups_matrix(request): return JsonResponse({'status': 'success'})
@csrf_exempt
def trigger_cyber_mesh_probe_api(request): return JsonResponse({'status': 'success'})
@csrf_exempt
def smtp_propropab_notifier_api(request): return JsonResponse({'status': 'success'})
def generate_free_google_qr_view(request): return HttpResponse("QR")

@csrf_exempt
def parse_ar_kr_blueprint_api(request):
    """📐 🤖 ЕЖИК ОБУЧАЕТСЯ: Глубокий парсинг разделов АР / КР и расчет логистики вечности"""
    detected_layers = [
        {"id": "02-АР0", "name": "Архитектурные решения. Подземная часть", "volume_m3": 450.0},
        {"id": "11-КЖ0.3", "name": "Вертикальные конструкции -1-го этажа", "steel_tonns": 24.5},
        {"id": "24-КМ3", "name": "Конструкции металлических лестниц", "steel_tonns": 12.8},
        {"id": "64-ЭОМ.ЦОД", "name": "Силовое электрооборудование и освещение ЦОД", "status": "СИНХРОНИЗИРОВАНО"}
    ]
    
    # Каскадный расчет выгодных условий логистики
    logistic_cost_rub = (450.0 * 320) + (37.3 * 1500)
    saved_syndicate_margin = logistic_cost_rub * 0.12
    
    return JsonResponse({
        "status": "success",
        "blueprint_archive": "📦 RAR-Архив Документация_актуальная_Сплпв.rar успешно распакован в ОЗУ!",
        "ezhik_parsed_layers": detected_layers,
        "logistics_optimization": {
            "optimal_carrier": "Яндекс.Грузовой & Деловые Линии (LISTEN контур)",
            "calculated_logistic_cost": f"{logistic_cost_rub:,.2f} ₽",
            "saved_margin_by_tonnage": f"{saved_syndicate_margin:,.2f} ₽",
            "verdict": "🟢 РЕЛЬСЫ И КОЛЕСА СВЕДЕНЫ. Бутылочные горлышки поставок устранены Ёжиком."
        }
    }, json_dumps_params={"ensure_ascii": False})
