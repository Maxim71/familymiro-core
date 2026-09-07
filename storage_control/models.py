# -*- coding: utf-8 -*-
from django.db import models

class Agreement(models.Model):
    agreement_number = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

class VideoCapsule(models.Model):
    video_title = models.TextField()
    video_file = models.CharField(max_length=500, blank=True, null=True)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return self.video_title[:50]

class BloggerUsage(models.Model):
    blogger_name = models.CharField(max_length=100, default="max_kosarev")
    daily_limit = models.IntegerField(default=12)
    accumulated_income = models.DecimalField(max_digits=15, decimal_places=2, default=15000000.00)
    accessible_capsules = models.ManyToManyField(VideoCapsule, blank=True)

    def __str__(self):
        return self.blogger_name

class FamilyLegacy(models.Model):
    """[👑 РОДОВАЯ ПАМЯТЬ ПОКОЛЕНИЙ] Хранилище имён, детских фраз Мирославы и слов Отца"""
    entity_name = models.CharField(max_length=255, default="Мирослава Косарева")
    record_type = models.CharField(max_length=100, default="Детское слово") # детское слово / отцовское наставление / имя рода
    text_content = models.TextField() # Сама фраза
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.entity_name} - {self.record_type}"

class AvatarEzhik(models.Model):
    status = models.CharField(max_length=100, default="Active_2026")
    profit_alerts = models.CharField(max_length=255, default="Lava Pay Active")

class InteractiveComment(models.Model):
    category_type = models.CharField(max_length=50, default="news")
    title = models.CharField(max_length=255, default="")
    comment_text = models.TextField(default="")
    is_approved_by_ezhik = models.BooleanField(default=False)

class ConstructionCompany(models.Model):
    company_name = models.CharField(max_length=255, default="РосКапиталСтрой")
    total_budget = models.DecimalField(max_digits=15, decimal_places=2, default=15000000.00)

class CascadeTask(models.Model):
    task_title = models.CharField(max_length=255)
    task_detail = models.TextField()
    target_role = models.CharField(max_length=50)

class PunchListItem(models.Model):
    description = models.TextField()
    is_fixed = models.BooleanField(default=False)

class NetworkIncident(models.Model):
    user_ip = models.GenericIPAddressField(default="127.0.0.1")
    country = models.CharField(max_length=100, default="Российская Федерация")
    timestamp = models.DateTimeField(auto_now_add=True)
    detected_intent = models.TextField(default="Scan")
    manager_comment = models.TextField(blank=True, null=True)
    reviewer_role = models.CharField(max_length=50, default="РУКОВОДИТЕЛЬ ПРОЕКТА")
    ezhik_verdict = models.TextField(default="Ждем проверки.")
