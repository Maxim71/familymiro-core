# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User

class ITRMember(models.Model):
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
        ("BUYER_B2B", "Покупатель / Заказчик снабжения"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="itr_profile")
    role = models.CharField(max_length=20, choices=ROLES, verbose_name="Должность/Статус")
    balance_rub = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Баланс счета")
    telegram_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="ID Telegram")

    def __str__(self):
        return f"{self.user.username} [{self.get_role_display()}]"

class MaterialCertificate(models.Model):
    material_name = models.CharField(max_length=255, verbose_name="Материал")
    certificate_number = models.CharField(max_length=100, unique=True, verbose_name="Номер сертификата")
    passport_file_url = models.URLField(blank=True, null=True, verbose_name="Ссылка на Паспорт качества")
    verified_by_qa = models.BooleanField(default=False, verbose_name="Проверено Инженером СКК")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Сертификат: {self.material_name} (№ {self.certificate_number})"

class DXFBlueprintLayer(models.Model):
    blueprint_name = models.CharField(max_length=255, verbose_name="Имя файла чертежа")
    layer_name = models.CharField(max_length=100, verbose_name="Имя CAD-слоя")
    detected_materials = models.JSONField(verbose_name="Физические объемы слоя (ИИ-Парсинг)")
    verified_by = models.ForeignKey(ITRMember, on_delete=models.SET_NULL, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Ювелирно выпрямляем календарную скобку вечности
        return f"{self.blueprint_name} -> {self.layer_name} [{self.updated_at.strftime('%Y-%m-%d')}]"

class PTOResourceJournal(models.Model):
    project_name = models.CharField(max_length=255, verbose_name="Объект стройки")
    active_zone = models.CharField(max_length=255, verbose_name="Где сейчас идут работы")
    machinery_hours = models.JSONField(verbose_name="Учет техники и моточасов")
    cascade_resource_data = models.JSONField(verbose_name="Каскад привлеченных данных")
    anchored_certificates = models.ManyToManyField(MaterialCertificate, blank=True, verbose_name="Ссылки-якоря на Паспорта")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Журнал: {self.project_name} -> {self.active_zone}"

class ExecutiveAnalytics(models.Model):
    viewer_role = models.CharField(max_length=50, verbose_name="Кто залогинился")
    income_optimization = models.TextField(verbose_name="Где доход")
    seo_meta_tags = models.JSONField(verbose_name="Мета-аналитика")
    future_plans_json = models.JSONField(verbose_name="Планы")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Бизнес-Анализ для {self.viewer_role} — {self.updated_at.strftime('%Y-%m-%d')}"

class ITRCalendarEvent(models.Model):
    member = models.ForeignKey(ITRMember, on_delete=models.CASCADE, related_name="calendar_events", verbose_name="Владелец календаря")
    event_title = models.CharField(max_length=255, verbose_name="Событие (Дедлайн/ТТН/Смета)")
    target_date = models.DateField(verbose_name="Дата события")
    ezhik_ai_marker = models.CharField(max_length=255, verbose_name="Разметка/Рекомендация Ёжика")
    is_completed = models.BooleanField(default=False, verbose_name="Статус выполнения")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.member.role}] {self.event_title} на {self.target_date.strftime('%Y-%m-%d')} — Метка: {self.ezhik_ai_marker}"

class FastResolutionPin(models.Model):
    issue_cipher = models.CharField(max_length=100, verbose_name="Шифр замечания / Коллизии")
    resolution_template = models.TextField(verbose_name="Готовое ИИ-решение для ПТО")
    attached_passport = models.ForeignKey(MaterialCertificate, on_delete=models.SET_NULL, null=True, blank=True)
    is_applied = models.BooleanField(default=False, verbose_name="Применено в ИД")

    def __str__(self):
        return f"Пин Решения для {self.issue_cipher}"

class EzhikSmartTask(models.Model):
    object_name = models.CharField(max_length=255, verbose_name="Наименование ИТР-Объекта")
    task_description = models.TextField(verbose_name="Техническое задание")
    initial_volume = models.FloatField(verbose_name="Исходный объем из IFC (м3/м.п.)")
    corrected_by_ezhik = models.FloatField(verbose_name="Скорректировано ИИ Ёжика")
    last_modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Задание: {self.object_name} (Правка ИИ: {self.corrected_by_ezhik})"


# 🛸 РАСШИРЕННЫЙ ENTERPRISE-КОНТУР АДАПТАЦИИ ОБЪЕКТОВ ПОД СКЛАД И ПТО
class PartnerPin(models.Model):
    title = models.CharField(max_length=150, default="Ячейка Склада М19")
    code = models.CharField(max_length=50, unique=True, default="PIN-M19-01")
    price_rub = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    discount_value = models.IntegerField(default=2, verbose_name="Маржа синдиката %")
    
    def __str__(self):
        return f"{self.title} [{self.code}]"

class StoreOrder(models.Model):
    order_sku = models.CharField(max_length=50, default="MAT-001")
    buyer = models.CharField(max_length=150, default="Прораб Синдиката")
    pin_item = models.ForeignKey(PartnerPin, on_delete=models.SET_NULL, null=True, blank=True)
    volume = models.FloatField(default=1.0)
    is_paid = models.BooleanField(default=True, verbose_name="Проведено ПТО")
    ordered_at = models.DateTimeField(auto_now_add=True)

class GuestMediaLog(models.Model):
    session_key = models.CharField(max_length=100, default="SESSION-RAM-001")
    watched_trend = models.CharField(max_length=150, default="Входной контроль чертежей АР/КР")
    seo_source = models.CharField(max_length=100, default="WinRAR Шлюз")
    processed_by_yolo = models.BooleanField(default=True)
    entered_at = models.DateTimeField(auto_now_add=True)
