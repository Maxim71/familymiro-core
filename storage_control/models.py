from django.db import models






class ConstructionObject(models.Model):
    name = models.CharField("Название объекта", max_length=255)
    address = models.CharField("Адрес площадки", max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name

class SpaceTransferAct(models.Model):
    construction_object = models.ForeignKey(ConstructionObject, on_delete=models.CASCADE, verbose_name="Объект")
    subcontractor_name = models.CharField("Субподрядная организация", max_length=255)
    floor = models.CharField("Этаж / Уровень", max_length=50, blank=True, null=True)
    axes = models.CharField("Привязка по осям", max_length=100, blank=True, null=True)
    room = models.CharField("Номер помещения / Позиция", max_length=100, blank=True, null=True)
    description = models.TextField("Описание фронта работ")
    created_at = models.DateTimeField("Дата составления", auto_now_add=True)
    chief_approved = models.BooleanField("Виза Начальника Участка", default=False)
    chief_approved_at = models.DateTimeField("Время согласования", blank=True, null=True)
    def __str__(self): return f"Акт Фронта №{self.id} — {self.subcontractor_name}"

class MaterialM15Invoice(models.Model):
    act_link = models.ForeignKey(SpaceTransferAct, on_delete=models.CASCADE, verbose_name="Привязка к Акту", blank=True, null=True)
    material_name = models.CharField("Наименование материала", max_length=255)
    unit = models.CharField("Единица измерения", max_length=50, default="куб.м")
    quantity = models.DecimalField("Переданный объем", max_digits=10, decimal_places=2)
    sender_name = models.CharField("Отпустил (Прораб)", max_length=150)
    receiver_name = models.CharField("Получил (Субподряд)", max_length=150)
    is_signed_by_chief = models.BooleanField("Утверждено Начучастка", default=False)
        # Добавь эти три строки внутрь класса MaterialM15Invoice, прямо перед def __str__(self):
    passport_required = models.BooleanField("Запрос паспорта изделия (ПТО)", default=False)
    passport_file_url = models.CharField("Ссылка на скачанный PDF сертификат", max_length=500, blank=True, null=True)
    passport_status = models.CharField("Статус проверки ГОСТ", max_length=100, default="Не затребован")

    def __str__(self): return f"М-15 №{self.id} — {self.material_name}"
    

class WarehouseStock(models.Model):
    """Текущие остатки на складе холдинга в реальном времени"""
    material_name = models.CharField("Материал", max_length=255, unique=True)
    quantity = models.DecimalField("Запасы на складе", max_digits=10, decimal_places=2)
    unit = models.CharField("Ед. изм.", max_length=50, default="куб.м")
    in_transit = models.DecimalField("В пути (скоро поступит)", max_digits=10, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self): return f"{self.material_name}: {self.quantity} {self.unit}"

class SupplyRequest(models.Model):
    """Заявки прорабов на день наперед (Стиль Ванкувер)"""
    STATUS_CHOICES = [
        ('pending', 'На согласовании (3 дня)'),
        ('approved', 'Утверждено / Тайм-слот выдан'),
        ('deficit', 'Отсутствует / Срочный дозаказ'),
        ('discrepancy', 'Акт несоответствия (Пересортица)'),
    ]
    construction_object = models.ForeignKey(ConstructionObject, on_delete=models.CASCADE)
    material_name = models.CharField("Материал", max_length=255)
    quantity_requested = models.DecimalField("Требуемый объем", max_digits=10, decimal_places=2)
    target_date = models.DateField("Дата поставки (на день наперед)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"Заявка №{self.id} — {self.material_name} ({self.status})"

class EzhikRouteCard(models.Model):
    """Оптимальные ИИ-карты маршрутов Робота-Ёжика"""
    request_link = models.OneToOneField(SupplyRequest, on_delete=models.CASCADE)
    route_map_data = models.TextField("Оптимальный маршрут (Тула - Объект)")
    assigned_driver = models.CharField("Водитель снабжения", max_length=150)
    is_dispatched = models.BooleanField("Задание направлено", default=False)
    def __str__(self): return f"Маршрут Ёжика для Заявки №{self.request_link.id}"
