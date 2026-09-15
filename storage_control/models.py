from django.db import models

class ConstructionObject(models.Model):
    """Глобальные строительные объекты холдинга"""
    name = models.CharField("Название ИТ-Объекта / Холдинга", max_length=255)
    country = models.CharField("Страна присутствия", max_length=100, default="Россия")
    city = models.CharField("Город / Локация матрицы", max_length=100, default="Тула")
    address = models.CharField("Адрес площадки", max_length=500)
    object_capital = models.DecimalField("Капитал объекта / Бюджет", max_digits=15, decimal_places=2, default=15000000.00)
    currency = models.CharField("Валюта расчетов", max_length=10, default="RUB")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.name} [{self.city}, {self.country}]"

class SpaceTransferAct(models.Model):
    """Акты фронта работ по осям и этажам"""
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
    """Накладные М-15 и СБП-инвойсы"""
    act_link = models.ForeignKey(SpaceTransferAct, on_delete=models.CASCADE, verbose_name="Привязка к Акту", blank=True, null=True)
    material_name = models.CharField("Наименование материала", max_length=255)
    unit = models.CharField("Единица измерения", max_length=50, default="куб.м")
    quantity = models.DecimalField("Переданный объем", max_digits=10, decimal_places=2)
    sender_name = models.CharField("Отпустил (Прораб)", max_length=150)
    receiver_name = models.CharField("Получил (Субподряд)", max_length=150)
    is_signed_by_chief = models.BooleanField("Утверждено Начучастка", default=False)
    passport_required = models.BooleanField("Запрос паспорта изделия (ПТО)", default=False)
    passport_file_url = models.CharField("Ссылка на скачанный PDF сертификат", max_length=500, blank=True, null=True)
    passport_status = models.CharField("Статус проверки ГОСТ", max_length=100, default="Не затребован")
    def __str__(self): return f"М-15 №{self.id} — {self.material_name}"

class WarehouseStock(models.Model):
    """Текущие остатки на складе холдинга"""
    material_name = models.CharField("Материал", max_length=255, unique=True)
    quantity = models.DecimalField("Запасы на складе", max_digits=10, decimal_places=2)
    unit = models.CharField("Ед. изм.", max_length=50, default="куб.м")
    in_transit = models.DecimalField("В пути", max_digits=10, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self): return f"{self.material_name}: {self.quantity} {self.unit}"

class SupplyRequest(models.Model):
    """Заявки прорабов на день наперед"""
    construction_object = models.ForeignKey(ConstructionObject, on_delete=models.CASCADE)
    material_name = models.CharField("Материал", max_length=255)
    quantity_requested = models.DecimalField("Требуемый объем", max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"Заявка №{self.id} — {self.material_name}"

class PartnerProduct(models.Model):
    """Товары партнеров в B2B-Магазине"""
    title = models.CharField("Наименование товара", max_length=255)
    price = models.DecimalField("Цена за единицу", max_digits=10, decimal_places=2)
    unit = models.CharField("Единица измерения", max_length=50, default="шт")
    partner_name = models.CharField("Поставщик / Партнер", max_length=150)
    image_url = models.CharField("Ссылка на картинку/гифку товара", max_length=500, default="/static/img/default_prod.png")
    sales_count = models.IntegerField("Счетчик общих покупок", default=142)
    def __str__(self): return f"{self.title} — {self.partner_name}"

class CartItem(models.Model):
    """Суверенная Корзина Снабженца"""
    product = models.ForeignKey(PartnerProduct, on_delete=models.CASCADE)
    quantity = models.IntegerField("Количество", default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.product.title} x {self.quantity}"

class LiveStreamMessage(models.Model):
    """Живой перехват сообщений в стерео-потоке"""
    sender_name = models.CharField("Имя", max_length=150)
    message_text = models.TextField("Сообщение")
    ezhik_reply = models.TextField("Ответ Ёжика", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"Поток от {self.sender_name}"

class ItrProrabTest(models.Model):
    """ЦЕПОЧКА РАСШИРЕНИЯ // ЖУРНАЛ ВХД И 4 ИТР-ФОТОФИКСАЦИИ ПРОРАБА"""
    prorab_name = models.CharField("ФИО Прораба (Линия)", max_length=150)
    work_stage = models.CharField("Этап / Вид строительных работ", max_length=255, default="Заливка плиты перекрытия")
    photo_1_axis = models.CharField("Фото 1: Оси", max_length=500, default="/static/img/axis.png")
    photo_2_reinforcement = models.CharField("Фото 2: Арматура", max_length=500, default="/static/img/arm.png")
    photo_3_shuttering = models.CharField("Фото 3: Опалубка", max_length=500, default="/static/img/shutter.png")
    photo_4_ready_work = models.CharField("Фото 4: Готовый вид", max_length=500, default="/static/img/ready.png")
    delivery_delay_detected = models.BooleanField("Нарушение сроков доставки", default=False)
    visible_defects_notes = models.TextField("Дефекты видимых работ", blank=True, null=True)
    aosr_generated = models.BooleanField("АОСР сгенерирован", default=True)
    defect_sheet_issued = models.BooleanField("Дефектная ведомость выписана", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"Журнал ВХД №{self.id} — {self.prorab_name}"
