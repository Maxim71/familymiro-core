# -*- coding: utf-8 -*-
from django.db import models

class Agreement(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True, verbose_name="Наименование соглашения")

class VideoCapsule(models.Model):
    capsule_id = models.CharField(max_length=100, blank=True, null=True)
    owner_name = models.CharField(max_length=100, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

class AvatarEzhik(models.Model):
    status = models.CharField(max_length=50)

class InteractiveComment(models.Model):
    text = models.TextField()

class BloggerUsage(models.Model):
    score = models.IntegerField(default=0)

class ConstructionCompany(models.Model):
    company_id = models.CharField(max_length=100, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    inn_code = models.CharField(max_length=100, blank=True, null=True)

class CascadeTask(models.Model):
    name = models.CharField(max_length=100)

class PunchListItem(models.Model):
    description = models.CharField(max_length=255)

class NetworkIncident(models.Model):
    incident_id = models.CharField(max_length=100, blank=True, null=True)
    node_name = models.CharField(max_length=100, blank=True, null=True)
    status_flag = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

# 🛍️ СУВЕРЕННАЯ СТРУКТУРА ТОВАРОВ МЕЗАНИНА С РУЧНОЙ ЗАГРУЗКОЙ КАРТИНОК И ФОТО
class MezaninProduct(models.Model):
    title = models.CharField(max_length=255, verbose_name="Наименование товара")
    source_platform = models.CharField(max_length=100, default="Суверенный Склад 🦾", verbose_name="Источник / Платформа")
    base_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Базовая цена (закупка)")
    margin_percent = models.IntegerField(default=20, verbose_name="Процент накрутки маржи (от 1 до 33)")
    delivery_days = models.IntegerField(default=7, verbose_name="Срок доставки в РФ (дней)")
    is_available = models.BooleanField(default=True, verbose_name="В наличии")
    image = models.ImageField(upload_to="products/", blank=True, null=True, verbose_name="Изображение товара")

    class Meta:
        verbose_name = "Товар Мезанина"
        verbose_name_plural = "Товары Мезанина"

    def __str__(self):
        return self.title

    @property
    def final_price(self):
        return round(float(self.base_price) * (1 + self.margin_percent / 100.0), 2)
