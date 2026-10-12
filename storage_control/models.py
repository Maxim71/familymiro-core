from django.db import models
from django.contrib.auth.models import User

class ITRMember(models.Model):
    """Полная инженерно-техническая структура строительной площадки"""
    ROLES = [
        ("CHIEF_ENG", "Главный инженер проекта / Нач. объекта"),
        ("SITE_CHIEF", "Начальник строительного участка"),
        ("FOREMAN", "Производитель работ (Прораб)"),
        ("MASTER", "Мастер строительно-монтажных работ"),
        ("PTO_CHIEF", "Начальник производственно-технического отдела"),
        ("PTO_ENG", "Инженер ПТО (Ведение ИД, Чертежи)"),
        ("ESTIMATOR", "Инженер-сметчик (Учет стоимости)"),
        ("GEODESIST", "Инженер-геодезист (Оси, Разбивка)"),
        ("ENERGY_ENG", "Главный энергетик (Силовые сети, ЭОМ)"),
        ("MECH_ENG", "Главный механик (Строительные машины, КМ)"),
        ("QA_ENG", "Инженер контроля качества (Строительный контроль)"),
        ("BIM_COORD", "Специалист информационного моделирования (BIM/IFC)"),
        ("HSE_ENG", "Специалист по охране труда"),
        # Новые роли Клиентов и Покупателей в B2B-магазине
        ("BUYER_B2B", "Покупатель / Заказчик снабжения"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="itr_profile")
    role = models.CharField(max_length=20, choices=ROLES, verbose_name="Должность/Статус")
    balance_rub = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Баланс счета")
    telegram_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="ID Telegram")

    def __str__(self):
        return f"{self.user.username} [{self.get_role_display()}]"

class PartnerPin(models.Model):
    """Пины/Товары в Магазине для Партнеров и Блогеров"""
    code = models.CharField(max_length=50, unique=True, verbose_name="Промокод / Пин")
    title = models.CharField(max_length=255, default="Пин скидки", verbose_name="Название товара")
    price_rub = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00, verbose_name="Цена в магазине")
    discount_value = models.DecimalField(max_digits=4, decimal_places=2, default=0.10, verbose_name="Размер скидки")

    def __str__(self):
        return f"{self.title} ({self.code})"

class StoreOrder(models.Model):
    """Заказы покупателей в Магазине Пинов"""
    buyer = models.ForeignKey(ITRMember, on_delete=models.CASCADE, related_name="orders", verbose_name="Покупатель")
    pin_item = models.ForeignKey(PartnerPin, on_delete=models.CASCADE, verbose_name="Купленный Пин")
    ordered_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата заказа")
    is_paid = models.BooleanField(default=False, verbose_name="Статус оплаты")

    def __str__(self):
        return f"Заказ №{self.id} — {self.buyer.user.username}"

class GuestMediaLog(models.Model):
    """SEO и Хронология отдыха Гостей под Режиссером (Просмотры трендов/блогверов)"""
    session_key = models.CharField(max_length=255, unique=True, verbose_name="Ключ гостевой сессии")
    watched_trend = models.CharField(max_length=255, verbose_name="Просмотренный ИИ-тренд")
    seo_source = models.CharField(max_length=100, default="Google/Yandex SEO", verbose_name="Откуда пришел гость")
    entered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Гость {self.session_key[:8]} -> {self.watched_trend}"
