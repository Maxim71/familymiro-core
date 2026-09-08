# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User

class Agreement(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)

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

# 🏢 КОНТУР ЗАСТРОЙЩИКОВ ТУЛЫ
class ConstructionCompany(models.Model):
    company_name = models.CharField(max_length=255, verbose_name="Наименование застройщика")
    inn_code = models.CharField(max_length=100, verbose_name="ИНН компании")

    def __str__(self):
        return self.company_name

# 🛍️ ТОВАРЫ МЕЗАНИНА С НАКРУТКОЙ МАРЖИ ОТ 1% ДО 33%
class MezaninProduct(models.Model):
    title = models.CharField(max_length=255, verbose_name="Наименование товара")
    source_platform = models.CharField(max_length=100, default="Суверенный Склад 🦾")
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    margin_percent = models.IntegerField(default=20)
    delivery_days = models.IntegerField(default=7)
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to="products/", blank=True, null=True)

    def __str__(self):
        return self.title

    @property
    def final_price(self):
        return round(float(self.base_price) * (1 + self.margin_percent / 100.0), 2)

# 🧾 Отношение МНОГИЕ К ОДНОМУ (ForeignKey): Много инвойсов привязаны к одному Застройщику
class AutoInvoice(models.Model):
    company = models.ForeignKey(ConstructionCompany, on_delete=models.CASCADE, verbose_name="Строительная Компания (Many-to-One)")
    invoice_number = models.CharField(max_length=100, verbose_name="Номер инвойса")
    created_at = models.DateTimeField(auto_now_add=True)
    
    # 🛒 Отношение МНОГИЕ КО МНОГИМ (ManyToManyField): Много инвойсов содержат много товаров Мезанина
    products = models.ManyToManyField(MezaninProduct, verbose_name="Товары в инвойсе (Many-to-Many)")

    def __str__(self):
        return self.invoice_number
