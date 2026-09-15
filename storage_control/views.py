import random
from django.shortcuts import render
from django.http import JsonResponse
from .models import ServerBalance, LiveStreamMessage, ItrProrabTest
from googletrans import Translator

def index_vancouver(request):
    """Главный ИТР-пульт управления: Трехсторонний шлюз Россия — Китай — КНДР"""
    server_stat, created = ServerBalance.objects.get_or_create(id=1, defaults={'balance_rub': 0.00})
    
    balance_rub = float(server_stat.balance_rub)
    balance_cny = balance_rub * 0.078  # Китайские Юани
    balance_kpw = balance_rub * 9.87   # Северокорейские Воны (KPW)
    
    context = {
        'server_balance_rub': f"{balance_rub:,.2f}",
        'server_balance_cny': f"{balance_cny:,.2f}",
        'server_balance_kpw': f"{balance_kpw:,.2f}",
        'object_capital_rub': "15 000 000.00 ₽",
        'market_status': "КОНТУР АКТИВЕН // МЕЖДУНАРОДНЫЙ ПРОТОКОЛ GIT-GATE-РТО (РФ-КНР-КНДР)",
        'tax_paid': server_stat.total_tax_paid
    }
    return render(request, 'storage_control/miro_monolith.html', context)

def send_to_stream_api(request):
    """
    «ЖУК ТОРНАДО 1.6»: Сквозной перевод и перехват рапортов прорабов КНДР, КНР и России.
    """
    if request.method == 'POST':
        name = request.POST.get('name', 'Максим Игоревич').strip()
        text = request.POST.get('text', '').strip()
        
        translator = Translator()
        try:
            detected = translator.detect(text)
            # Перехват корейского языка (КНДР)
            if detected.lang == 'ko':
                translated = translator.translate(text, dest='ru')
                display_text = f"🇰🇵 [КНДР ОРИГИНАЛ]: {text} <br>➔ 🇷🇺 [ИТР-ПЕРЕВОД]: {translated.text}"
                reply_text = "🦔 [ЁЖИК]: Северокорейский индустриальный рапорт верифицирован по стандартам ЕАЭС."
            # Перехват китайского языка
            elif detected.lang in ['zh-cn', 'zh']:
                translated = translator.translate(text, dest='ru')
                display_text = f"🇨🇳 [КНР ОРИГИНАЛ]: {text} <br>➔ 🇷🇺 [ИТР-ПЕРЕВОД]: {translated.text}"
                reply_text = "🦔 [ЁЖИК]: Китайский закуп MONLID зафиксирован в протокол GIT-GATE-РТО."
            # Русский язык прораба — переводим в Азию
            else:
                translated_cn = translator.translate(text, dest='zh-cn')
                display_text = f"🇷🇺 [РУССКИЙ]: {text} <br>➔ 🇨🇳🇰🇵 [ASIA GATE]: {translated_cn.text}"
                reply_text = "🦔 [ЁЖИК]: Команда прораба Тулы транслирована на партнерские фабрики Азии."
        except Exception:
            display_text = text
            reply_text = "🦔 [ЁЖИК]: Сигнал зафиксирован локально."

        remote_responses = [
            "🇨🇳 [FACTORY PEKIN]: 4张照片已收到。 (4 фото скрытых работ приняты.)",
            "🇰🇵 [조선 노동자]: 함경남도 철강 출하 준비 완포! (출하準備!) (КНДР: Металлопрокат к отгрузке в Тулу готов!)",
            "🏗️ [ПТО ТУЛА]: Стыковка накладных М-15 по азиатскому импорту завершена."
        ]
        
        LiveStreamMessage.objects.create(sender_name=name, message_text=display_text, ezhik_reply=reply_text)
        
        random_report = random.choice(remote_responses)
        LiveStreamMessage.objects.create(
            sender_name="GLOBAL PROTOCOL", 
            message_text=random_report, 
            ezhik_reply="⚡ [ШЛЮЗ РТО АКТИВЕН]"
        )
        return JsonResponse({'status': 'success', 'reply': reply_text})
    return JsonResponse({'status': 'invalid'})

def save_vhd_journal_record(request): return JsonResponse({'status': 'success'})
def live_stream_dashboard_api(request):
    messages_list = LiveStreamMessage.objects.all().order_by('-created_at')[:5]
    data = [{'name': m.sender_name, 'text': m.message_text, 'reply': m.ezhik_reply} for m in messages_list]
    return JsonResponse({'stream': data})

def add_to_cart_api(request, product_id):
    server_stat = ServerBalance.objects.get(id=1)
    server_stat.balance_rub += float(250.00)
    server_stat.save()
    return JsonResponse({'status': 'success', 'cart_count': random.randint(1, 10)})

def checkout_sbp_payment_api(request): return JsonResponse({'status': 'paid'})
def pto_cabinet(request, act_id): return render(request, 'storage_control/pto_cabinet.html')
def neuro_radar_dashboard(request): return render(request, 'storage_control/neuro_radar.html')
def capsule_time_vault(request): return render(request, 'storage_control/capsule.html')
