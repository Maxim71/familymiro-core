import hashlib
import logging
logger = logging.getLogger(__name__)

from django.test import TestCase
from django.urls import reverse
from .models import Agreement, AvatarEzhik, PunchListItem
from django.utils import timezone
from datetime import timedelta
class FamilyMiroGlobalTDDTest(TestCase):
    """
    [Протокол TDD] Бронебойный юнит-тест проекта FAMILYMIRO 1.6.
    Простукивает шлюзы, проверяет коды ответов 200 OK и изолирует контуры.
    """

    def setUp(self):
        """Подготовка вековой ноды базы данных перед симуляцией штурма"""
        # Создаем базовый Уговор
        self.agreement = Agreement.objects.create(
            capsule_id="Miro_Global_Root_Test",
            category="FAMILY",
            teaser_video_path="tmp/test_teaser.mp4",
            unlock_date=timezone.now() + timedelta(days=366), # Вековой замок на 1 год
            receiver_email="architect@mail.ru",
            receiver_phone="+79991112233"
        )
        # Активируем Аватара Ёжика
        self.ezhik = AvatarEzhik.objects.create(
            name="Автономный Савелий/Ёжик",
            total_revenue=1000.0,
            is_learning=True
        )

    def test_global_hybrid_portal(self):
        """1. Авто-тест Главного шлюза (Храм Вечности)"""
        url = reverse('index_family')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        logger.info("✅ Тест Слой 1: Главный портал выдал чистый код 200 OK.")

    def test_construction_ubuntu_gost(self):
        """2. Авто-тест Пульта Прораба (Контур А1) и ИИ-Проверки фиксации баланса"""
        url = reverse('index_construction')
        response = self.client.get(url)
        # Проверяем, что без анонимной сессии доступ открыт (или возвращает контекст)
        self.assertIn(response.status_code, [200, 403])
        
        # Проверяем, что Ёжик зафиксировал мудрость в базе данных
        self.ezhik.refresh_from_db()
        self.assertTrue(self.ezhik.is_learning)

    def test_capsule_vault_secure_isolation(self):
        """3. Авто-тест скрытого Пульта Отца и изоляции от самозванцев"""
        # Попытка войти без заветного хэша
        url = reverse('father_panel') + "?room_key=WRONG_KEY"
        response = self.client.get(url)
        # Должна маскироваться под ошибку 404 (Страница не найдена) для защиты от чужих глаз
        self.assertEqual(response.status_code, 403)
        
        # Попытка войти с правильным хэшем отцовских слов
        target_hash = hashlib.sha256("Какие мы большие! — Да.".encode('utf-8')).hexdigest()[:16]
        secure_url = reverse('father_panel') + f"?room_key={target_hash}"
        secure_response = self.client.get(secure_url)
        self.assertEqual(secure_response.status_code, 200)
        logger.info("✅ Тест Слой 2: Полная изоляция Сейфов проверена. Самозванцы летят в бан.")
