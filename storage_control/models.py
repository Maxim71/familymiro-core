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


class BloggerStreamLog(models.Model):
    """Трансляции Блогеров, мобильный плеер и учет анонимных донатов"""
    streamer_name = models.CharField(max_length=255, verbose_name="Имя стримера/Блогера")
    trending_tag = models.CharField(max_length=100, verbose_name="Трендовый тег (#BIM_Stroyka)")
    donation_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Сумма доната (RUB)")
    is_anonymous = models.BooleanField(default=True, verbose_name="Услуга анонимности")
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Стрим {self.streamer_name} — Донат {self.donation_amount} RUB"

class BIMModelCollision(models.Model):
    """Зрение Сокола: Фиксация инженерных коллизий чертежей (ПТО/BIM/Геодезия)"""
    blueprint_layer = models.CharField(max_length=255, verbose_name="Контур/Слой чертежа")
    collision_description = models.TextField(verbose_name="Описание пересечения осей")
    detected_by = models.ForeignKey(ITRMember, on_delete=models.SET_NULL, null=True, related_name="detected_collisions")
    is_resolved = models.BooleanField(default=False, verbose_name="Исправлено прорабом")
    detected_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Коллизия {self.blueprint_layer} — Статус: {self.is_resolved}"

class TimeCapsuleInvestment(models.Model):
    """Финансовый сейф ВЕЧНОСТИ: Вклады и брокерские счета детям сквозь года"""
    parent_user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Отправитель (Папа)")
    allocated_funds = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Завещаемый капитал (RUB)")
    lock_term_years = models.IntegerField(choices=[(3, "3 года"), (5, "5 лет"), (30, "30 лет")], verbose_name="Срок капсулы")
    yield_rate_p_a = models.DecimalField(max_digits=5, decimal_places=2, default=23.50, verbose_name="Динамический процент ЦБ")
    legal_protection_active = models.BooleanField(default=True, verbose_name="Юридический щит активен")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Капсула на {self.lock_term_years} лет — {self.allocated_funds} RUB"


class MaterialCertificate(models.Model):
    """Сертификаты и паспорта качества на расходные материалы площадки"""
    material_name = models.CharField(max_length=255, verbose_name="Материал")
    certificate_number = models.CharField(max_length=100, unique=True, verbose_name="Номер сертификата")
    passport_file_url = models.URLField(blank=True, null=True, verbose_name="Ссылка на Паспорт качества")
    verified_by_qa = models.BooleanField(default=False, verbose_name="Проверено Инженером СКК")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Сертификат: {self.material_name} (№ {self.certificate_number})"

class FlexibleTimeCapsule(models.Model):
    """Гибкая капсула времени: Срок выбирает сам Пользователь (Медиа: Фото/Видео/Голос)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Отправитель")
    delivery_date = models.DateField(verbose_name="Точная дата вскрытия капсулы")
    wishes_text = models.TextField(blank=True, null=True, verbose_name="Текстовое пожелание")
    attached_media_url = models.URLField(blank=True, null=True, verbose_name="Медиавложение (Изображение/Видео/Голос)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Капсула {self.user.username} до {self.delivery_date}"

class TIMCascadeAnalysis(models.Model):
    """BIM / TIM и формат IFC: Каскадный анализ динамики расчета выгоды"""
    project_cipher = models.CharField(max_length=100, verbose_name="Шифр ТИМ-проекта")
    ifc_file_path = models.CharField(max_length=255, verbose_name="Путь к файлу IFC/DWG")
    cascade_profit_rub = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Рассчитанная выгода каскада")
    ezhik_proposal = models.TextField(verbose_name="Предложение и аналитический ответ Ёжика")
    export_excel_url = models.URLField(verbose_name="Выгрузка графиков в Excel/DWG")

    def __str__(self):
        return f"ТИМ-Анализ {self.project_cipher} — Выгода: {self.cascade_profit_rub} RUB"
