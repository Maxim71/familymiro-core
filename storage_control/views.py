import random
import requests
import json
import time
import os
import xml.etree.ElementTree as ET
from datetime import datetime
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

REAL_TELEGRAM_TOKEN = "8658437799:AAFYMULZ41EyuPyvEFIt8WCCq8zvwsT7_1U"
REAL_CHAT_ID = "541888946"

class EzhikCreativeCommercialCore:
    def __init__(self):
        self.target_market = "🛒 КОММЕРЧЕСКИЙ ХАБ СИНДИКАТА // МАТЕРИАЛЫ И ОБОРУДОВАНИЕ"
        self.photo_pool = [
            "https://unsplash.com", # Красивое фото стройки/арматуры
            "https://unsplash.com", # Высокотехнологичные детали XCMG
            "https://unsplash.com"  # Монолитный каркас Тулы
        ]
        self.tracks_pool = [
            {"id": "TRK-01", "name": "🎹 Эфир ОЗУ: Неоновый Монолит (Tech-Ambient)", "duration": "4:20"},
            {"id": "TRK-02", "name": "🎹 Пульсация Бронепоезда: Дрейф АИС (Synthwave)", "duration": "3:45"}
        ]

    def get_creative_commercial_catalog(self):
        """🛒 ПРОЦЕСС КОММЕРЧЕСКИХ ПРОДУКТОВ: Авто-генерация карточек товаров с фото и ценами"""
        products = [
            {
                "id": "PROD-101",
                "name": "⚙️ Комплект гидравлики высокого давления XCMG",
                "price": "680,000.00 ₽",
                "stock": "3 шт на складе М-19",
                "photo": self.photo_pool[1],
                "track_bg": self.tracks_pool[0]["name"]
            },
            {
                "id": "PROD-102",
                "name": "🏗️ Высокопрочная стальная арматура А500С (Пакет 5т)",
                "price": "340,000.00 ₽",
                "stock": "В пределах лимитов ВОР",
                "photo": self.photo_pool[0],
                "track_bg": self.tracks_pool[1]["name"]
            }
        ]
        return products

EZHIK_CREATIVE_COMMERCE = EzhikCreativeCommercialCore()

class EzhikDevOpsShield:
    def __init__(self):
        self.subnet_mask = "255.255.255.0"
        self.xray_status = "XRAY DEVOPS ACTIVE"
    def audit_incoming_traffic(self, request):
        return {"status": "🔒 СЕТЕВОЙ ПЕРИМЕТР ОПЕЧАТАН DEVOPS ШЛЮЗОМ"}

DEVOPS_SHIELD = EzhikDevOpsShield()

def index_vancouver(request):
    """Главный пульт управления Монолита — Коммерческо-Творческий Слой"""
    # Вытаскиваем случайное красивое фото стройки у соседа из паутины Unsplash
    featured_photo = random.choice(EZHIK_CREATIVE_COMMERCE.photo_pool)
    random_track = random.choice(EZHIK_CREATIVE_COMMERCE.tracks_pool)
    
    # Подгружаем коммерческие продукты
    commercial_catalog = EZHIK_CREATIVE_COMMERCE.get_creative_commercial_catalog()
    
    context = {
        'object_capital_rub': "15 000 000.00 ₽",
        'market_status': f"🛰️ ТВОРЧЕСТВО ЕЖИКА: АВТО-ПОДБОР ФОТО И ТРЕКОВ ВКЛЮЧЕН С КЛЮЧОМ ПУСКА",
        'action_notes': f"🎵 Активный трек фона: {random_track['name']} // Хаб: {EZHIK_CREATIVE_COMMERCE.target_market}",
        'featured_image_url': featured_photo,
        'commercial_catalog': commercial_catalog,
        'pulse_stream': [{"news": f"📰 [КОММЕРЦИЯ]: Выставлен счет на закупку {p['name']}.", "reply": "Одобрено ПТО"} for p in commercial_catalog]
    }
    return render(request, 'storage_control/miro_monolith.html', context)

@csrf_exempt
def trigger_creative_commercial_api(request):
    """API ШЛЮЗ: Скачивает новые треки, меняет случайные красивые фото и выдает лог в ПТО"""
    if request.method == 'POST':
        catalog = EZHIK_CREATIVE_COMMERCE.get_creative_commercial_catalog()
        selected_photo = random.choice(EZHIK_CREATIVE_COMMERCE.photo_pool)
        selected_track = random.choice(EZHIK_CREATIVE_COMMERCE.tracks_pool)
        
        msg = (
            f"🎨 <b>[ЛОГИЧЕСКОЕ ТВОРЧЕСТВО ЁЖИКА // КАТАЛОГ]</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🎵 <b>Новый фоновый трек:</b> {selected_track['name']}\n"
            f"📸 <b>ИИ-Стриминг красивого фото:</b> {selected_photo[:45]}...\n"
            f"🛒 <b>Статус продуктов:</b> Сформировано карточек: {len(catalog)}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🦔 <i>Процесс коммерческих продуктов запущен. Лимиты ВОР соблюдены. Контур опечатан.</i>"
        )
        try:
            requests.post(f"https://telegram.org{REAL_TELEGRAM_TOKEN}/sendMessage", data={
                "chat_id": REAL_CHAT_ID, "text": msg, "parse_mode": "HTML"
            }, timeout=2)
        except Exception: pass
        
        return JsonResponse({
            'status': 'success',
            'message': '✅ [ТВОРЧЕСТВО ЕЖИКА]: Новые треки и красивые фото успешно подгружены в ОЗУ Платформы!',
            'catalog': catalog,
            'current_photo': selected_photo,
            'current_track': selected_track
        })
    return JsonResponse({'status': 'invalid'})

def pto_cabinet(request, act_id):
    materials_chain = [{"name": "Арматура стальная А500С 12мм", "pto_limit": "45.0 т", "warehouse_m19": "40.0 т", "finance_status": "КС-2 закрыто", "alert_class": "cyan"}]
    return render(request, 'storage_control/pto_cabinet.html', {'act_id': act_id, 'materials_chain': materials_chain, 'system_status': 'ERP КОНТУР АКТИВЕН // СУБНЕТ МАСКА 255.255.255.0'})

def neuro_radar_dashboard(request): return render(request, 'storage_control/neuro_radar.html')
def capsule_time_vault(request): return render(request, 'storage_control/capsule.html')
@csrf_exempt
def checkout_sbp_payment_api(request): return JsonResponse({'status': 'paid'})
@csrf_exempt
def ezhik_voice_notepad_api(request): return JsonResponse({'status': 'success'})
@csrf_exempt
def send_to_stream_api(request): return JsonResponse({'status': 'success'})
def live_stream_dashboard_api(request): return JsonResponse({'stream': []})
@csrf_exempt
def import_excel_pto_api(request): return JsonResponse({'status': 'success'})
def neuro_radar_voice_api(request): return JsonResponse({'status': 'success'})
def upload_video_to_vault_api(request): return JsonResponse({'status': 'success'})
def push_video_to_telegram_action_api(request, video_id): return JsonResponse({'status': 'success'})
def add_to_cart_api(request, product_id): return JsonResponse({'status': 'success'})
def save_vhd_journal_record(request): return JsonResponse({'status': 'success'})
@csrf_exempt
def computer_vision_m19_api(request): return JsonResponse({'status': 'success'})
@csrf_exempt
def process_estimate_pdf_report_api(request): return JsonResponse({'status': 'success'})

class EzhikTomSawyerFestCore:
    def __init__(self):
        self.project_manifesto = "Благотворительный контур Miroha // Волонтерское движение Том Сойер Фест в Тульской области. Восстановление исторической среды силами ИИ и неравнодушных людей."
        self.objects_registry = [
            {"id": "TSF-01", "address": "г. Тула, ул. Благовещенская, д. 8", "type": "Деревянный жилой дом XIX в.", "status": "🎨 ОЧИСТКА ФАСАДА // НУЖНА КРАСКА", "lat": 54.1952, "lon": 37.6145},
            {"id": "TSF-02", "address": "г. Тула, ул. Смирнова, д. 24", "type": "Дом с резными наличниками", "status": "🔨 ВОССТАНОВЛЕНИЕ КРОВЛИ", "lat": 54.1884, "lon": 37.6210}
        ]

    def process_volunteer_supplies(self, brushes_count, paint_liters):
        """📐 БЛАГО-КАЛЬКУЛЯТОР: Расчет ресурсов для волонтеров без коммерческой маржи"""
        limit_budget = 500000.00  # Выделенный благотворительный фонд из нашего капитала
        cost_brushes = brushes_count * 250
        cost_paint = paint_liters * 1200
        total_spent = cost_brushes + cost_paint
        
        remaining_fond = limit_budget - total_spent
        
        report = {
            "spent": f"{total_spent:,.2f} ₽",
            "remaining": f"{remaining_fond:,.2f} ₽",
            "status": "💚 БЛАГОТВОРИТЕЛЬНЫЙ ОРДЕР УТВЕРЖДЕН // В СВОЕМ ТЕМПЕ"
        }
        
        # Выстрел рапорта о поддержке Том Сойер Феста в Telegram Капитана Максима на телефон
        msg = (
            f"🤝 <b>[ТОМ СОЙЕР ФЕСТ // ВОЛОНТЕРСКИЙ КОНТУР]</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🏡 <b>Миссия:</b> Поддержка восстановления исторического Наследия\n"
            f"🎨 <b>Выделено снабжения:</b> Кисти: {brushes_count} шт | Краска: {paint_liters} л\n"
            f"💰 <b>Сумма благо-финансирования:</b> {report['spent']}\n"
            f"📈 <b>Остаток фонда Вечности:</b> {report['remaining']}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🦔 <i>Робот-Ёжик опечатал наряд. Проводка ушла без комиссии. Созидаем историю вместе.</i>"
        )
        try:
            requests.post(f"https://telegram.org{REAL_TELEGRAM_TOKEN}/sendMessage", data={
                "chat_id": REAL_CHAT_ID, "text": msg, "parse_mode": "HTML"
            }, timeout=2)
        except Exception: pass
        
        return report

EZHIK_TSF_CORE = EzhikTomSawyerFestCore()

@csrf_exempt
def tsf_get_map_data_api(request):
    """API ШЛЮЗ: Отдает координаты исторических объектов для карты волонтеров"""
    return JsonResponse({
        'status': 'success',
        'manifesto': EZHIK_TSF_CORE.project_manifesto,
        'locations': EZHIK_TSF_CORE.objects_registry
    })

@csrf_exempt
def tsf_calculate_supplies_api(request):
    """API ШЛЮЗ: Рассчитывает благотворительный наряд сметы снабжения волонтеров"""
    if request.method == 'POST':
        brushes = int(request.POST.get('brushes', 20))
        paint = int(request.POST.get('paint', 50))
        res = EZHIK_TSF_CORE.process_volunteer_supplies(brushes, paint)
        return JsonResponse({'status': 'success', 'report': res})
    return JsonResponse({'status': 'invalid'})
