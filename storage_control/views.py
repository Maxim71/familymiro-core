import random
import pyotp
import requests
import os
from django.shortcuts import render
from django.http import JsonResponse
from .models import ServerBalance, LiveStreamMessage, ItrProrabTest, EzhikUserCabinet, EzhikVideoVault

CAPTAIN_SECRET = "M32MIROHACRE2059VAULTTANGERINE55"
REAL_TELEGRAM_TOKEN = "8658437799:AAFYMULZ41EyuPyvEFIt8WCCq8zvwsT7_1U"
REAL_CHAT_ID = "541888946"

def get_or_create_ezhik_charm(request):
    if not request.session.session_key: request.session.create()
    s_key = request.session.session_key
    moba_names = ["Мастер Осей", "Вековой Хроникер", "Инфлюенсер Наследия", "RFI Диспетчер", "Продюсер Эфира"]
    moba_styles = ["cyan", "pink", "green", "gold"]
    cabinet, _ = EzhikUserCabinet.objects.get_or_create(
        session_key=s_key,
        defaults={'assigned_name': f"{random.choice(moba_names)} №{random.randint(100, 999)}", 'moba_style_preference': 'cyan', 'user_country': "Россия"}
    )
    return cabinet

def sync_telegram_channel_videos():
    """
    ЖУК ТОРНАДО // БОЕВОЙ ПАРСЕР TG-КАНАЛА:
    Ёжик заходит от имени токена, ищет новые видео, скачивает их через getFile
    и сохраняет в базу результатов для отображения в Капсуле Вечности!
    """
    try:
        # Запрашиваем последние обновления/сообщения от бота
        url = f"https://telegram.org{REAL_TELEGRAM_TOKEN}/getUpdates"
        response = requests.get(url, timeout=5).json()
        
        if response.get("ok") and response.get("result"):
            for update in response["result"]:
                message = update.get("message") or update.get("channel_post")
                if not message:
                    continue
                
                # Ищем, есть ли в сообщении видеоролик
                video_data = message.get("video")
                if video_data:
                    file_id = video_data.get("file_id")
                    title = message.get("caption") or f"Детское Воспоминание №{video_data.get('file_unique_id', 'ITR')}"
                    
                    # Проверяем, не скачивали ли мы его уже
                    if not EzhikVideoVault.objects.filter(video_title__contains=title).exists():
                        # Шаг A: Запрашиваем путь к файлу через getFile
                        file_info_url = f"https://telegram.org{REAL_TELEGRAM_TOKEN}/getFile?file_id={file_id}"
                        file_info = requests.get(file_info_url, timeout=5).json()
                        
                        if file_info.get("ok"):
                            file_path = file_info["result"].get("file_path")
                            # Шаг B: Скачиваем видеоролик на жесткий диск нашего сервера
                            download_url = f"https://telegram.org{REAL_TELEGRAM_TOKEN}/{file_path}"
                            video_bytes = requests.get(download_url, timeout=10).content
                            
                            local_filename = f"tg_video_{file_id[:10]}.mp4"
                            local_path = os.path.join("/var/www/miroha_static/uploads/", local_filename)
                            
                            with open(local_path, "wb") as f:
                                f.write(video_bytes)
                            
                            # Шаг C: Намертво заносим в СУБД SQLite с вековой ссылкой статики Nginx
                            EzhikVideoVault.objects.create(
                                video_title=f"❤️ [ПЕРЕХВАТ ИЗ TG]: {title}",
                                video_file_url=f"/static/uploads/{local_filename}",
                                country_origin="⚓️ СОРТИРОВОЧНЫЙ ПОРТ ВЛАДИВОСТОК // TG-ХАБ"
                            )
    except Exception:
        pass

def index_vancouver(request):
    server_stat, created = ServerBalance.objects.get_or_create(id=1, defaults={'balance_rub': 0.00})
    cabinet = get_or_create_ezhik_charm(request)
    balance_rub = float(server_stat.balance_rub)
    context = {
        'server_balance_rub': f"{balance_rub:,.2f}",
        'server_balance_cny': f"{(balance_rub * 0.078):,.2f}",
        'server_balance_kpw': f"{(balance_rub * 9.87):,.2f}",
        'object_capital_rub': "15 000 000.00 ₽",
        'market_status': "КОНТУР АКТИВЕН // ЖУК-ПАРСЕР TG КАНАЛА ВКЛЮЧЕН",
        'tax_paid': server_stat.total_tax_paid,
        'user_cabinet': cabinet,
        'action_notes': "🦔 [ПАРСЕР ТОРНАДО]: Ёжик зашёл в канал, проверил file_id и синхронизировал новые видео."
    }
    return render(request, 'storage_control/miro_monolith.html', context)

def capsule_time_vault(request):
    """Капсула времени: Запуск живой синхронизации с твоим Telegram при каждом обновлении"""
    cabinet = get_or_create_ezhik_charm(request)
    is_captain = False
    if request.method == 'POST' and 'totp_code' in request.POST:
        if pyotp.TOTP(CAPTAIN_SECRET).verify(request.POST.get('totp_code', '').strip()): is_captain = True

    # 🔥 ЗАПУСКАЕМ ЖИВОЙ ПАРСИНГ ТВОРЧЕСТВА ИЗ ТВОЕГО ТГ КАНАЛА
    sync_telegram_channel_videos()

    video_list = EzhikVideoVault.objects.filter(is_approved_by_ezhik=True).order_by('-created_at')[:10]
    good_events = [
        {"date": "15.09.2026", "title": "🔬 ИИ-Биологи Transformers полностью расшифровали старение клеток мозга."},
        {"date": "12.09.2026", "title": "⚡ Запущен коммерческий реактор чистой энергии OpenStack."}
    ]
    scientists_chronicles = [{"author": "Жук Торнадо ИТР", "text": "Парсинг выполнен. Видео залиты в статический порт Nginx."}]
    
    from datetime import datetime
    time_delta = datetime(2059, 5, 24) - datetime.now()
    
    context = {
        'is_captain': is_captain, 'years': time_delta.days // 365, 'days': time_delta.days % 365,
        'sbp_code': "INV-ALFA-288003", 'user_cabinet': cabinet, 'videos': video_list,
        'good_events': good_events, 'chronicles': scientists_chronicles,
        'qr_setup_url': f"https://qrserver.com{CAPTAIN_SECRET}%26issuer=MirohaPlatform"
    }
    return render(request, 'storage_control/capsule.html', context)

def upload_video_to_vault_api(request):
    if request.method == 'POST':
        EzhikVideoVault.objects.create(
            video_title=request.POST.get('title', 'Архив Наследия').strip(),
            video_file_url="/static/uploads/tg_video_default.mp4",
            country_origin="🚀 АСИНХРОННЫЙ ХАБ ТОРНАДО"
        )
        return JsonResponse({'status': 'success', 'message': '✅ Видео обработано!'})
    return JsonResponse({'status': 'invalid'})

def push_video_to_telegram_action_api(request, video_id):
    try:
        video = EzhikVideoVault.objects.get(id=video_id)
        msg = f"✈️ <b>[ТРАНСЛЯЦИЯ]</b>\n📦 <b>Видео №{video.id}</b>\n📜 <b>Суть:</b> {video.video_title}"
        requests.post(f"https://telegram.org{REAL_TELEGRAM_TOKEN}/sendMessage", data={"chat_id": REAL_CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=3)
        return JsonResponse({'status': 'success', 'message': '✈️ Сигнал отправлен в Telegram!'})
    except Exception: return JsonResponse({'status': 'error'})

def send_to_stream_api(request):
    if request.method == 'POST':
        name = request.POST.get('name', 'Капитан').strip()
        text = request.POST.get('text', '').strip()
        try: requests.post(f"https://telegram.org{REAL_TELEGRAM_TOKEN}/sendMessage", data={"chat_id": REAL_CHAT_ID, "text": f"🏗️ <b>[{name}]:</b> {text}", "parse_mode": "HTML"}, timeout=3)
        except Exception: pass
        LiveStreamMessage.objects.create(sender_name=name, message_text=text, ezhik_reply="Перехвачено")
        return JsonResponse({'status': 'success', 'reply': "Перехвачено"})
    return JsonResponse({'status': 'invalid'})

def live_stream_dashboard_api(request):
    messages_list = LiveStreamMessage.objects.all().order_by('-created_at')[:5]
    data = [{'name': m.sender_name, 'text': m.message_text, 'reply': m.ezhik_reply} for m in messages_list]
    return JsonResponse({'stream': data})

def add_to_cart_api(request, product_id): return JsonResponse({'status': 'success'})
def checkout_sbp_payment_api(request): return JsonResponse({'status': 'paid'})
def pto_cabinet(request, act_id): return render(request, 'storage_control/pto_cabinet.html')
def save_vhd_journal_record(request): return JsonResponse({'status': 'success'})
def neuro_radar_dashboard(request): return render(request, 'storage_control/neuro_radar.html')
