from django.db import models
from django.contrib.auth.models import User

class BloggerProfile(models.Model):
    """Профиль Блогера в ИТР-платформе (Учет реального заработка)"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='blogger_profile')
    channel_name = models.CharField(max_length=255, verbose_name="Название канала/блога")
    total_earned_rub = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Всего заработано (RUB)")
    balance_payout_ready = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Доступно к выводу")

    def __str__(self):
        return f"Блогер: {self.channel_name} ({self.user.username})"

class PartnerPin(models.Model):
    """Магазин Пинов (Скидки от партнеров + привязка к блогерам)"""
    PIN_TYPES = [
        ('LOGISTICS', 'Скидка на логистику и доставку'),
        ('MATERIAL', 'Скидка на расходные материалы'),
        ('LABOR', 'Бонусные человеко-часы ИТР'),
    ]
    code = models.CharField(max_length=50, unique=True, verbose_name="Промокод / Пин")
    blogger = models.ForeignKey(BloggerProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='pins')
    pin_type = models.CharField(max_length=20, choices=PIN_TYPES, default='MATERIAL')
    discount_value = models.DecimalField(max_digits=4, decimal_places=2, help_text="Например, 0.15 для 15%")
    blogger_commission_rub = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00, help_text="Сколько получает блогер за активацию")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Пин {self.code} (-{self.discount_value * 100}%)"

class WarehouseMaterial(models.Model):
    """Склад учета расходных материалов для СТРОЙКИ"""
    MATERIAL_STATUS = [
        ('OK', 'В достатке на складе'),
        ('LOW', 'Заканчивается / Нужно заказать'),
        ('ORDERED', 'Заказано / Едет на объект'),
    ]
    name = models.CharField(max_length=255, verbose_name="Наименование материала")
    cipher = models.CharField(max_length=50, verbose_name="Шифр ИТР (АР/КЖ/ЭОМ)")
    image_url = models.URLField(blank=True, null=True, verbose_name="Изображение материала (Pinterest-стиль)")
    quantity_available = models.FloatField(default=0.00, verbose_name="Доступно на складе (Кладовщик принял)")
    quantity_required_by_spec = models.FloatField(default=0.00, verbose_name="Необходимо по спецификации чертежа")
    status = models.CharField(max_length=15, choices=MATERIAL_STATUS, default='OK')

    def __str__(self):
        return f"{self.name} [{self.cipher}] — {self.quantity_available} шт."

class PinActivationLog(models.Model):
    """Хронология объединений ИД: Фиксация активации пина прорабом"""
    pin = models.ForeignKey(PartnerPin, on_delete=models.CASCADE)
    foreman = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Прораб / Инженер")
    project_cipher = models.CharField(max_length=100, verbose_name="Шифр ИД объекта")
    activated_at = models.DateTimeField(auto_now_add=True)
    money_allocated_to_blogger = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        """Режиссер автоматизации: при сохранении акта начисляет деньги блогеру в базу"""
        if not self.pk and self.pin.blogger:
            blogger_prof = self.pin.blogger
            commission = self.pin.blogger_commission_rub
            blogger_prof.total_earned_rub += commission
            blogger_prof.balance_payout_ready += commission
            blogger_prof.save()
            self.money_allocated_to_blogger = True
        super().save(*args, **kwargs)
