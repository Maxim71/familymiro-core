# -*- coding: utf-8 -*-
from django.db import models

class Agreement(models.Model):
    title = models.CharField("Название соглашения/оферты", max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.title

class VideoCapsule(models.Model):
    video_title = models.CharField("Название ролика TikTok/YouTube", max_length=200)
    video_file = models.FileField("Видеофайл OpenCV/FFmpeg", upload_to="videos/", blank=True, null=True)
    is_public = models.BooleanField("Доступно для SHOP", default=False)
    def __str__(self): return self.video_title

class AvatarEzhik(models.Model):
    status = models.CharField("Текущий Статус ИИ", max_length=100, default="Active_2026")
    opencv_logs = models.TextField("Логи Нейро-Радара OpenCV", blank=True, null=True)
    ai_recommendations = models.TextField("Рекомендации Ёжика Хозяйке", blank=True, null=True)
    profit_alerts = models.TextField("Уведомления о прибыли Lava Pay ('лаве')", blank=True, null=True)
    def __str__(self): return f"Статус Ёжика: {self.status}"

class InteractiveComment(models.Model):
    CONTENT_TYPES = [('news', 'Новость'), ('snip', 'СНиП Ссылка'), ('poetry', 'Стихи')]
    category_type = models.CharField("Категория", max_length=20, choices=CONTENT_TYPES, default='news')
    title = models.CharField("Заголовок находки", max_length=250)
    comment_text = models.TextField("Очищенный текст материала")
    is_approved_by_ezhik = models.BooleanField("Одобрено в печать", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"[{self.category_type}] {self.title[:30]}"

class BloggerUsage(models.Model):
    blogger_name = models.CharField("Имя Блогера / ИТР", max_length=150)
    daily_limit = models.IntegerField("Лимит медиа в день", default=12)
    accumulated_income = models.DecimalField("Заработанное 'лаве' (%)", max_digits=12, decimal_places=2, default=0.00)
    def __str__(self): return f"Магазин: {self.blogger_name}"


# ==============================================================================
# 🏗️ НОВЫЕ БРОНИРОВАННЫЕ МОДЕЛИ B2B КАСКАДА ДЛЯ КОРПОРАТИВНЫХ КЛИЕНТОВ
# ==============================================================================

class ConstructionCompany(models.Model):
    """Строительная компания, купившая лицензию на платформу"""
    company_name = models.CharField("Название Холдинга/Компании", max_length=200, unique=True)
    license_status = models.BooleanField("Лицензия Активна", default=True)
    total_budget = models.DecimalField("Глобальный Бюджет Холдинга", max_digits=15, decimal_places=2, default=0.00)
    
    def __str__(self): return self.company_name

class CascadeTask(models.Model):
    """Каскад упорядочивания задач Ёжика: сбор, анализ и статусы для ИТР ролей"""
    ROLE_CHOICES = [
        ('director', 'Директор Холдинга (Глобальный контроль)'),
        ('manager', 'Руководитель проекта (Управление объектом)'),
        ('prorab', 'Прораб на участке (Исполнение в зоне)'),
    ]
    company = models.ForeignKey(ConstructionCompany, on_delete=models.CASCADE, verbose_name="Компания/Объект")
    target_role = models.CharField("Для какой роли задача", max_length=20, choices=ROLE_CHOICES)
    task_title = models.CharField("Суть задачи / Наряд", max_length=250)
    task_detail = models.TextField("Инструкция и ведомость СНиП")
    
    # Рекомендации и анализ от Ёжика под капотом
    ezhik_ai_analysis = models.TextField("Анализ рисков и предложение Ёжика", blank=True, null=True)
    
    is_completed = models.BooleanField("Статус выполнения", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return f"[{self.get_target_role_display()}] {self.task_title[:30]}"

class PunchListItem(models.Model):
    """Связываем дефекты и снабжение прорабов с каскадом задач"""
    task = models.ForeignKey(CascadeTask, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Привязанный наряд каскада")
    defect_description = models.TextField("Дефект или объём заливки бетона")
    paint_barrels = models.IntegerField("Закупка бочек краски (шт)", default=0)
    is_fixed = models.BooleanField("Верифицировано OpenCV (ГОСТ 475-2016)", default=False)
    def __str__(self): return self.defect_description[:30]
