import os
import sys
import django

# Намертво блокируем ошибку AppRegistryNotReady (строки 1-5)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from storage_control.models import Agreement, PunchListItem

class FamilyMiroCentralGateway:
    def __init__(self, qr_payload: dict):
        """
        qr_payload: Данные, считанные с Главного QR-кода на фронтенде платформы.
        Пример: {"target": "heritage", "capsule_id": "MIRO-2026"} или {"target": "gost_control"}
        """
        self.payload = qr_payload
        self.target = qr_payload.get("target", "unknown")

    def route_stream(self):
        """Центральный распределитель потоков if/elif (Архитектура 1.5)"""
        
        # 1. Поток НАСЛЕДНИКИ (Django Сейф + Гренландский Храм Любви)
        if self.target == "heritage" or self.target == "family_safe":
            capsule_id = self.payload.get("capsule_id")
            agreement = Agreement.objects.filter(capsule_id=capsule_id, is_public=False).first()
            
            if not agreement:
                return {"status": 404, "style_mode": "family", "action": "BLOCK", "message": "Сейф невидим!"}
                
            return {
                "status": 200,
                "style_mode": "family",  # Сигнал фронтенду включить Гренландию
                "microservice": "Django (Core)",
                "endpoint": f"/api/safe/capsule/{capsule_id}/",
                "secure": "Binary Vector Active"
            }

        # 2. Поток ТИКТОКЕРЫ (Kivy + Реактивный Неоновый Интерфейс Загрузки)
        elif self.target == "tiktok_upload" or self.target == "neuro_director":
            capsule_id = self.payload.get("capsule_id")
            agreement = Agreement.objects.filter(capsule_id=capsule_id).first()
            
            # Жесткое табу на экспорт личных семейных капсул в TikTok API
            if agreement and not agreement.is_public:
                return {"status": 403, "style_mode": "tiktok", "action": "TABOO", "message": "Экспорт заблокирован ИИ!"}

            return {
                "status": 200,
                "style_mode": "tiktok",  # Сигнал фронтенду зажечь Неон
                "microservice": "Kivy Mobile App",
                "action": "Trigger OpenCV & FFmpeg Audio-Ducking Engine"
            }

        # 3. Поток СТРОИТЕЛИ (Flask VIP-Кабинет + Строгий Стальной Пульт СНиП)
        elif self.target == "gost_control" or self.target == "builder_cabinet":
            items_count = PunchListItem.objects.count()
            return {
                "status": 200,
                "style_mode": "gost",  # Сигнал фронтенду включить Сталь
                "microservice": "Flask Cabinet",
                "endpoint": "/builder/dashboard/",
                "context_data": f"Total PunchList Items: {items_count}"
            }

        # Неизвестный поток / Защита от ботов ведомств
        else:
            return {"status": 404, "style_mode": "default", "action": "MASK_AS_404"}


import os
import sys
import django
from django.utils import timezone

# Принудительная инициализация Джанго, чтобы не было ошибок импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
try:
    django.setup()
except Exception:
    pass

from storage_control.models import Agreement, PunchListItem

class FamilyMiroCentralGateway:
    def __init__(self, qr_data: dict):
        """
        qr_data: пакет данных, прилетевший со считывателя QR-кода.
        Пример: {"type": "media"} или {"type": "heritage", "capsule_id": "MIRO-2059"}
        """
        self.qr_data = qr_data
        self.stream_type = qr_data.get("type", "viral")

    def route_user_stream(self):
        """Центральный распределитель «Мега-Входа» (Архитектура 1.5)"""
        
        # ДОРОГА 1: ВИДЕО-МАНЫ И БЛОГЕРЫ (Виральный бесплатный космос)
        if self.stream_type == "media" or self.stream_type == "viral":
            return {
                "status": 200,
                "redirect_url": "/tiktok/", # Перенос в ультрафиолетовый смартфон
                "style_mode": "tiktok",
                "message": "Вход 'Одним желанием' разрешён. Доступ к ИИ-сжатию открыт."
            }

        # ДОРОГА 2: СТРОИТЕЛИ И ПРОРАБЫ (Платный контур СНиП + Альфа-СБП)
        elif self.stream_type == "construction" or self.stream_type == "gost":
            # Проверяем, есть ли закрытые дефекты на объекте
            defects_count = PunchListItem.objects.filter(is_closed=False).count()
            return {
                "status": 200,
                "redirect_url": "/construction/", # Перенос на Стальной пульт
                "style_mode": "gost",
                "payment_required": True, # Сигнал включить оранжевый блок монетизации
                "info": f"Активных дефектов на объекте контроля: {defects_count}"
            }

        # ДОРОГА 3: СЕЙФ ПАМЯТИ И ВЕКОВОЙ БУДИЛЬНИК (Наследники)
        elif self.stream_type == "heritage":
            capsule_id = self.payload.get("capsule_id", "MIRO-2059")
            agreement = Agreement.objects.filter(capsule_id=capsule_id).first()
            
            if not agreement:
                return {"status": 404, "message": "Капсула времени не найдена на Складе."}
                
            # Проверяем вековой Будильник
            is_unlocked = timezone.now() >= agreement.unlock_date
            
            return {
                "status": 200,
                "redirect_url": "/", # Перенос в Храм Наследия Лики
                "style_mode": "family",
                "is_unlocked": is_unlocked,
                "alarm_time": agreement.unlock_date.strftime("%d.%m.%Y %H:%M"),
                "message": "Считывание векового QR-Маяка прошло успешно. Запуск MediaPipe ID-Scan..."
            }

        # ЗАЩИТА ОТ БОТОВ ВЕДОМСТВ: Маскируемся под ошибку 404
        else:
            return {"status": 404, "message": "Страница не найдена."}
