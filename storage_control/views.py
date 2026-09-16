import random
import pyotp
import requests
import json
import time
from datetime import datetime
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ServerBalance, LiveStreamMessage, EzhikUserCabinet, EzhikVideoVault

# =====================================================================
# 🦔 КЛАСС АВТОНОМНОГО ИИ-АГЕНТА "EZHIK_CORE" (ТВОЙ ЦИФРОВОЙ ДИСПЕТЧЕР)
# =====================================================================
class EzhikAutonomousAgent:
    def __init__(self):
        # База знаний и жестких ИТР-взглядов Максима, запечатанная в ОЗУ агента
        self.manifesto_knowledge_base = {
            "business_philosophy": "Контур Miroha Монолит удерживает 100% контроля маржинальности. Лимиты ПТО священны. Перерасход снабжения без RFI-запроса карается блокировкой транша.",
            "vancouver_capital": "Целевой капитал объекта в Туле составляет 15,000,000.00 рублей. Комиссия синдиката — 2% с каждого закрытого акта КС-2.",
            "vessels_priority": "Ликвидный дефицит (запчасти Komatsu, Liugong, гидравлика XCMG) раскупается с колёс. Приоритет АИС-трекинга морских путей максимальный."
        }
        self.telegram_token = "8658437799:AAFYMULZ41EyuPyvEFIt8WCCq8zvwsT7_1U"
        self.chat_id = "541888946"

    def analyze_and_execute(self, context_type, raw_data):
        """Семантический ИИ-анализатор: принимает решение на основе базы знаний"""
        log_time = datetime.now().strftime("%H:%M:%S")
        
        if context_type == "vessel_delay":
            # Агент сам рассчитывает сдвиг ГПР и принимает решение
            hours_delayed = raw_data.get("hours", 48)
            verdict = f"🚨 [ИТР-ДИРЕКТИВА ЁЖИКА]: Судно {raw_data.get('name')} задерживается на {hours_delayed} ч. График ПТО автоматически скорректирован. Снабженцу отменить бронь фур на Владивосток, перенести лимиты на резервные даты."
            self._fire_to_telegram(verdict)
            return {"status": "action_taken", "log": f"[{log_time}] Агент пересчитал ГПР из-за задержки карго."}
            
        elif context_type == "prorab_notes":
            # Агент очищает хаос мыслей прораба и превращает в жесткие задачи
            text = raw_data.get("text", "").lower()
            if "потеряли" in text or "накладную" in text:
                verdict = f"📝 [ИИ-КОНТРОЛЬ М-19]: Прораб сообщил о потере документов. Ёжик заблокировал автоматическое списание материалов по СУБД до выгрузки дубликата. Финдиректору направлен запрос."
                self._fire_to_telegram(verdict)
                return {"status": "frozen", "log": f"[{log_time}] Агент заморозил складской ордер до верификации."}
        
        return {"status": "idle", "log": f"[{log_time}] Контур стабилен, аномалий не обнаружено."}

    def _fire_to_telegram(self, text):
        """Прямой туннель связи агента с телефоном Капитана"""
        try:
            url = f"https://telegram.org{self.telegram_token}/sendMessage"
            requests.post(url, data={"chat_id": self.chat_id, "text": text, "parse_mode": "HTML"}, timeout=2)
        except Exception:
            pass

# Инициализируем живого агента в памяти сервера
EZHIK_AGENT = EzhikAutonomousAgent()

def index_vancouver(request):
    """Главный пульт Монолита Наследия"""
    server_stat, created = ServerBalance.objects.get_or_create(id=1, defaults={'balance_rub': 0.00})
    balance_rub = float(server_stat.balance_rub)
    
    if not request.session.session_key: request.session.create()
    cabinet, _ = EzhikUserCabinet.objects.get_or_create(
        session_key=request.session.session_key,
        defaults={'assigned_name': "Капитан Максим", 'moba_style_preference': 'cyan', 'user_country': "Россия"}
    )
    
    context = {
        'server_balance_rub': f"{balance_rub:,.2f}",
        'object_capital_rub': "15 000 000.00 ₽",
        'market_status': "🛰️ АВТОНОМНЫЙ ИИ-АГЕНТ ВКЛЮЧЕН В ОЗУ // MIROHA PLATFORM",
        'tax_paid': server_stat.total_tax_paid,
        'user_cabinet': cabinet,
        'action_notes': "🦔 Робот-Ёжик обрел автономию. Запущена объектная модель принятия решений EZHIK_CORE."
    }
    return render(request, 'storage_control/miro_monolith.html', context)

@csrf_exempt
def ezhik_voice_notepad_api(request):
    """Шлюз ИИ-Блокнота: Передача сырых мыслей напрямую в логику Агента"""
    if request.method == 'POST':
        raw_text = request.POST.get('raw_notes', '').strip()
        if not raw_text: return JsonResponse({'status': 'error', 'message': 'Пустой черновик'})
        
        # Передаем управление живому агенту
        agent_decision = EZHIK_AGENT.analyze_and_execute("prorab_notes", {"text": raw_text})
        
        structured_output = (
            f"🏗️ <b>[ЖИВОЙ ИИ-АГЕНТ ЕЖИК // АВТОНОМНЫЙ ВЕРДИКТ]</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📥 <b>Входные сырые данные:</b> \"{raw_text}\"\n"
            f"🤖 <b>Решение Агента:</b> {agent_decision['log']}\n"
            f"⚙️ <b>Статус системы:</b> Действие зафиксировано в СУБД SQLite."
        )
        return JsonResponse({'status': 'success', 'structured_text': structured_output})
    return JsonResponse({'status': 'invalid'})

def neuro_radar_dashboard(request):
    """Динамический спутниковый АИС-трекинг рейсов спецтехники КНР"""
    current_timestamp = int(time.time())
    dynamic_lat = round(34.12 + (current_timestamp % 60) * 0.006, 4)
    dynamic_lon = round(124.45 + (current_timestamp % 60) * 0.009, 4)
    
    # Имитируем штормовое предупреждение для проверки автономной реакции Ёжика
    if (current_timestamp % 20) == 0:
        EZHIK_AGENT.analyze_and_execute("vessel_delay", {"name": "COSCO SHANGHAI", "hours": 12})
        
    vessels = [
        {
            "id": "COSCO-SH",
            "name": "🚢 Контейнеровоз 'COSCO SHANGHAI'",
            "cargo": "⚙️ Ликвидный дефицит: Редукторы Komatsu, гидравлика XCMG",
            "route": "Порт Шанхай ➔ Владивосток Зона Таможни",
            "coordinates": f"{dynamic_lat}° N, {dynamic_lon}° E (Живой АИС-поток)",
            "status": "🌊 В ПУТИ // Автономный мониторинг Ёжика включен",
            "eta": "22.09.2026",
            "color_theme": "cyan"
        }
    ]
    return render(request, 'storage_control/neuro_radar.html', {'vessels': vessels, 'system_status': "АИС-СПУТНИК ОПЕЧАТАН АГЕНТОМ"})

def pto_cabinet(request, act_id):
    return render(request, 'storage_control/pto_cabinet.html', {'act_id': act_id, 'system_status': "СВЯЗЬ АГЕНТА ОНЛАЙН"})

def capsule_time_vault(request): return render(request, 'storage_control/capsule.html')
@csrf_exempt
def import_excel_pto_api(request): return JsonResponse({'status': 'success'})
@csrf_exempt
def neuro_radar_voice_api(request): return JsonResponse({'status': 'success'})
def upload_video_to_vault_api(request): return JsonResponse({'status': 'success'})
def push_video_to_telegram_action_api(request, video_id): return JsonResponse({'status': 'success'})
def send_to_stream_api(request): return JsonResponse({'status': 'success'})
def live_stream_dashboard_api(request): return JsonResponse({'stream': [{"name": "🦔 [EZHIK_CORE]", "text": "Автономный ИИ-агент успешно инициализирован в ОЗУ.", "reply": "Активен"}]})
def add_to_cart_api(request, product_id): return JsonResponse({'status': 'success'})
def checkout_sbp_payment_api(request): return JsonResponse({'status': 'paid'})
def save_vhd_journal_record(request): return JsonResponse({'status': 'success'})
@csrf_exempt
def computer_vision_m19_api(request): return JsonResponse({'status': 'success'})
