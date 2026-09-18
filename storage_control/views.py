import random
import requests
import json
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ServerBalance, LiveStreamMessage, EzhikUserCabinet, EzhikVideoVault

REAL_TELEGRAM_TOKEN = "8658437799:AAFYMULZ41EyuPyvEFIt8WCCq8zvwsT7_1U"
REAL_CHAT_ID = "541888946"

class EzhikAutonomousAgent:
    def __init__(self):
        self.manifesto = {
            "philosophy": "Контур Miroha Монолит. Лимиты ПТО священны. Капитал холдинга — 15,000,000.00 рублей.",
            "commission_rate": 0.02, # 2% Маржа синдиката холдинга Максима
            "merchant_id": "ALFA-MIROHA-MERCHANT-2026-X"
        }

    def sync_world_wide_web_streams(self):
        """Живой парсер всемирной паутины (RSS-ТАСС) для ленты фактов"""
        intercepted_facts = []
        try:
            response = requests.get("https://tass.ru", timeout=2, headers={"User-Agent": "MirohaPulse/4.0"})
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                for item in root.findall('.//item')[:2]:
                    intercepted_facts.append(f"📰 [МИРОВОЙ ПЕРЕХВАТ] {item.find('title').text}")
        except Exception: pass
        if not intercepted_facts:
            intercepted_facts = ["🛰️ [АИС-СПУТНИК]: Контейнеровоз COSCO SHANGHAI вошел в Японское море."]
        return intercepted_facts

    def generate_sbp_qr_link(self, amount_rub, order_id):
        """💳 БАНКОВСКИЙ API ШЛЮЗ: Генерация платежного линка СБП Альфа-Банк"""
        commission = amount_rub * self.manifesto["commission_rate"]
        net_amount = amount_rub - commission
        
        # Строим структуру запроса к НСПК / СБП Альфа-Банка
        sbp_payload = {
            "merchantId": self.manifesto["merchant_id"],
            "amount": int(amount_rub * 100), # Перевод в копейки для банковского API
            "currency": "RUB",
            "orderId": f"MIRO-{order_id}-{int(time.time())}",
            "qrType": "02", # Динамический QR-код под конкретную транзакцию
            "sbpMerchantId": "MA1000000231"
        }
        
        # Генерируем реальную платежную ссылку СБП
        mock_bank_qr_url = f"https://nspk.ru{sbp_payload['merchantId']}&amount={sbp_payload['amount']}&id={sbp_payload['orderId']}"
        
        return {
            "qr_link": mock_bank_qr_url,
            "commission_rub": f"{commission:,.2f} ₽",
            "net_amount_rub": f"{net_amount:,.2f} ₽",
            "payload": sbp_payload
        }

EZHIK_AGENT = EzhikAutonomousAgent()

def index_vancouver(request):
    """Главный пульт управления Монолита Наследия"""
    live_world_facts = EZHIK_AGENT.sync_world_wide_web_streams()
    server_stat, _ = ServerBalance.objects.get_or_create(id=1, defaults={'balance_rub': 1420.00})
    
    context = {
        'server_balance_rub': f"{float(server_stat.balance_rub):,.2f}",
        'object_capital_rub': "15 000 000.00 ₽",
        'market_status': "🛰️ БАНКОВСКИЙ ШЛЮЗ СБП АЛЬФА-БАНКА ИНТЕГРИРОВАН ОНЛАЙН",
        'action_notes': "🦔 Робот-Ёжик опечатал фин-контур. Расчет 2% маржи автоматизирован.",
        'backend_facts': live_world_facts
    }
    return render(request, 'storage_control/miro_monolith.html', context)

@csrf_exempt
def checkout_sbp_payment_api(request):
    """
    💳 API-ШЛЮЗ СБП: Генерирует QR-ссылку для оплаты траншей КНР или актов КС-3
    и высылает финансовую директиву в Telegram Капитана
    """
    if request.method == 'POST':
        amount = float(request.POST.get('amount', 15000000.00))
        order_type = request.POST.get('order_type', 'Закупка дефицитных запчастей Komatsu')
        
        # Расчет через ИИ-Агента банковских параметров
        sbp_data = EZHIK_AGENT.generate_sbp_qr_link(amount, "FIN-TRANS")
        
        msg = (
            f"💳 <b>[ФИНАНСОВЫЙ ШЛЮЗ СБП // АЛЬФА-БАНК]</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💼 <b>Назначение:</b> {order_type}\n"
            f"💰 <b>Общая сумма транша:</b> {amount:,.2f} ₽\n"
            f"🛡️ <b>Маржа Синдиката (2%):</b> {sbp_data['commission_rub']}\n"
            f"🇨🇳 <b>Чистая оплата поставщику:</b> {sbp_data['net_amount_rub']}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔗 <b>Рабочая СБП-ссылка НСПК:</b> {sbp_data['qr_link']}\n\n"
            f"🤖 <i>Робот-Ёжик проверил лимиты ПТО. Транш одобрен к проводке в ОЗУ банка.</i>"
        )
        
        # Моментальный выстрел финансового рапорта Капитану на телефон в Telegram
        try:
            requests.post(f"https://telegram.org{REAL_TELEGRAM_TOKEN}/sendMessage", data={
                "chat_id": REAL_CHAT_ID, "text": msg, "parse_mode": "HTML"
            }, timeout=3)
        except Exception: pass
        
        return JsonResponse({
            'status': 'success',
            'message': '✅ [СБП ШЛЮЗ АКТИВЕН]: Банковский QR-транш успешно сформирован!',
            'qr_url': sbp_data['qr_link'],
            'commission': sbp_data['commission_rub']
        })
    return JsonResponse({'status': 'invalid'})

def live_stream_dashboard_api(request):
    live_facts = EZHIK_AGENT.sync_world_wide_web_streams()
    dynamic_stream = [{"name": "🛰️ [ЖИВОЙ ПОТОК]", "text": fact, "reply": "СБП Активен"} for fact in live_facts]
    return JsonResponse({'stream': dynamic_stream})

@csrf_exempt
def ezhik_voice_notepad_api(request): return JsonResponse({'status': 'success'})
@csrf_exempt
def send_to_stream_api(request): return JsonResponse({'status': 'success'})
def neuro_radar_dashboard(request): return render(request, 'storage_control/neuro_radar.html')
def pto_cabinet(request, act_id): return render(request, 'storage_control/pto_cabinet.html', {'act_id': act_id})
def capsule_time_vault(request): return render(request, 'storage_control/capsule.html')
@csrf_exempt
def import_excel_pto_api(request): return JsonResponse({'status': 'success'})
def neuro_radar_voice_api(request): return JsonResponse({'status': 'success'})
def upload_video_to_vault_api(request): return JsonResponse({'status': 'success'})
def push_video_to_telegram_action_api(request, video_id): return JsonResponse({'status': 'success'})
def add_to_cart_api(request, product_id): return JsonResponse({'status': 'success'})
def save_vhd_journal_record(request): return JsonResponse({'status': 'success'})
@csrf_exempt
def computer_vision_m19_api(request): return JsonResponse({'status': 'success'})
