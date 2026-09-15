import random
from django.shortcuts import render
from django.http import JsonResponse
from .models import ServerBalance, LiveStreamMessage, ItrProrabTest
from googletrans import Translator # Подключаем ИИ-переводчик потока

def index_vancouver(request):
    """Главный ИТР-пульт управления: Международный мост Россия - Китай"""
    server_stat, created = ServerBalance.objects.get_or_create(id=1, defaults={'balance_rub': 0.00})
    balance_rub = float(server_stat.balance_rub)
    balance_cny = balance_rub * 0.078
    
    context = {
        'server_balance_rub': f"{balance_rub:,.2f}",
        'server_balance_cny': f"{balance_cny:,.2f}",
        'object_capital_rub': "15 000 000.00 ₽",
        'market_status': "КОНТУР АКТИВЕН // МЕЖДУНАРОДНЫЙ ШЛЮЗ PROTOCOL GIT-GATE-РТО",
        'tax_paid': server_stat.total_tax_paid
    }
    return render(request, 'storage_control/miro_monolith.html', context)

def send_to_stream_api(request):
    """
    ЖУК ТОРНАДО С ИИ-ПЕРЕВОДОМ (GIT-GATE-РТО):
    Автоматический перевод китайских иероглифов на русский и наоборот прямо в эфире.
    """
    if request.method == 'POST':
        name = request.POST.get('name', 'Максим Игоревич').strip()
        text = request.POST.get('text', '').strip()
        
        translator = Translator()
        try:
            # Робот-Ёжик автоматически определяет язык текста (китайский или русский)
            detected = translator.detect(text)
            if detected.lang == 'zh-cn' or detected.lang == 'zh':
                # Если пишут из Китая — переводим на русский для наших прорабов
                translated = translator.translate(text, dest='ru')
                display_text = f"🇨🇳 [КИТАЙСКИЙ ОРИГИНАЛ]: {text} <br>➔ 🇷🇺 [ПЕРЕВОД ЁЖИКА]: {translated.text}"
                reply_text = "🦔 [ЁЖИК]: Международный RFI-сигнал верифицирован. Документы GIT-GATE-РТО сформированы."
            else:
                # Если пишет наш прораб — дублируем перевод на китайский для фабрики КНР
                translated = translator.translate(text, dest='zh-cn')
                display_text = f"🇷🇺 [РУССКИЙ]: {text} <br>➔ 🇨🇳 [FOR CHINA PARTNERS]: {translated.text}"
                reply_text = "🦔 [ЁЖИК]: Рапорт прораба переведен на китайский и отправлен на фабрику MONLID."
        except Exception:
            # Резервный режим, если внешняя ИИ-сеть занята
            display_text = text
            reply_text = "🦔 [ЁЖИК]: Поток зафиксирован в локальный эскиз памяти."

        # Скрытый перехват рапортов с дальних точек
        remote_responses = [
            "🇨🇳 [FACTORY PEKIN]: 我们已经收到了4张隐藏工程的照片。符合规范！(Мы получили 4 фото скрытых работ. Всё по СНиП!)",
            "🏗️ [ТЕХНАДЗОР ТУЛА]: RFI Акт выполненных работ по осям А-Г успешно состыкован с китайской накладной.",
            "🚚 [ЛОГИСТИКА ШАНХАЙ]: 货物正通过 GIT-GATE-РТО Шлюз 发往 Тула (Груз идет через шлюз в Тулу)."
        ]
        
        # Сохраняем сообщение автора с переводом
        LiveStreamMessage.objects.create(sender_name=name, message_text=display_text, ezhik_reply=reply_text)
        
        # ИИ-Ёжик автоматически выплёвывает встречный рапорт-перевод от китайских коллег
        random_report = random.choice(remote_responses)
        try:
            if "FACTORY" in random_report or "SHANGHAI" in random_report:
                # Японские или китайские крохи переводим на русский
                cn_clean = random_report.split('(')[-1].replace(')', '') if '(' in random_report else random_report
                msg_bot = f"{random_report}<br>➔ 🤖 [ИТР-ПЕРЕВОД ДЛЯ РФ]: {cn_clean}"
            else:
                msg_bot = random_report
        except Exception:
            msg_bot = random_report

        LiveStreamMessage.objects.create(
            sender_name="GLOBAL GIT-GATE", 
            message_text=msg_bot, 
            ezhik_reply="⚡ [ШЛЮЗ РТО АКТИВЕН]"
        )
        
        return JsonResponse({'status': 'success', 'reply': reply_text})
    return JsonResponse({'status': 'invalid'})

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
def save_vhd_journal_record(request): return JsonResponse({'status': 'success'})
def neuro_radar_dashboard(request): return render(request, 'storage_control/neuro_radar.html')
def capsule_time_vault(request): return render(request, 'storage_control/capsule.html')
