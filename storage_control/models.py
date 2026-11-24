# -*- coding: utf-8 -*-
from django.db import models
import uuid
from urllib.parse import quote_plus
from django.contrib.auth.models import User


# 📊 ТОТАЛЬНЫЙ СУБД-РЕЕСТР 76 ГОСТ-НАПРАВЛЕНИЙ ЦОД НПО "СПЛАВ"
OFFICIAL_GOST_NORMS = {
    "01-ГП": "Генеральный план",
    "02-АР0": "Архитектурные решения. Подземная часть",
    "03-АР1.1": "Архитектурные решения. 1 этаж",
    "04-АР1.2": "Архитектурные решения. 2 этаж",
    "05-АР1.3": "Архитектурные решения. 3 этаж",
    "06-АР1.4": "Архитектурные решения. 4 этаж",
    "07-АР1.5": "Архитектурные решения. 5 этаж. Кровля",
    "08-АР2": "Архитектурные решения. Фасады. Разрезы.",
    "09-КЖ0.1": "Котлован",
    "10-КЖ0.2": "Бетонная подготовка и фундаментная плита",
    "11-КЖ0.3": "Вертикальные конструкции -1-го этажа",
    "12-КЖ0.4": "Плита перекрытия -1 этажа",
    "13-КЖ0.5": "Дренаж",
    "14-КЖ1": "Вертикальные конструкции 1-го этажа",
    "15-КЖ2": "Плита перекрытия 1-го этажа",
    "16-КЖ3": "Вертикальные конструкции 2, 3, 4 этажей",
    "17-КЖ4": "Плита перекрытия 2,3,4 этажей",
    "18-КЖ5": "Вертикальные конструкции 5 этажа",
    "19-КЖ6": "Плита покрытия",
    "20-КЖ7": "Конструкции надстроек на кровле и парапеты",
    "21-КЖ8": "Лестницы и промежуточные лестничные площадки",
    "22-КМ1": "Конструкции козырьков и крылец",
    "23-КМ2": "Конструкции ограждений",
    "24-КМ3": "Конструкции металлических лестниц",
    "25-ЭС.0.4кВ": "Электроснабжение (Кл 0.4 кВ)",
    "26-ЭС.6кВ": "Электроснабжение (Кл 6кВ)",
    "27-ЭН": "Наружное освещение",
    "28-ЭМ": "Силовое электрооборудование",
    "29-ЭО": "Электрическое освещение (внутреннее)",
    "30-ИТП.ЭОМ": "Индивидуальный тепловой пункт. Силовое электрооборудование",
    "31-НВ": "Наружное водоснабжение",
    "32-ВК1": "Внутренние системы водоснабжения",
    "33-ВК2": "Внутренние системы канализации",
    "34-НК": "Наружная канализация",
    "35-ДК": "Наружная дождевая канализация",
    "36-ОВ1": "Отопление и теплоснабжение",
    "37-ОВ2": "Общеобменная вентиляция и кондиционирование",
    "38-ПВ": "Противодымная вентиляция",
    "39-ИТП": "Индивидуальный тепловой пункт. Тепломеханика",
    "40-ИТП.УУТЭ": "Индивидуальный тепловой пункт. Узел учета тепловой энергии",
    "41-ТС": "Тепловые сети",
    "42-СКС": "Структурированная кабельная система",
    "43-ССМГН": "Двусторонняя диспетчерская связь с МГН",
    "44-СКК": "Система кабеленесущих конструкций",
    "45-СКС.СБ": "Сеть передачи данных для систем безопасности",
    "46-СС.СКУД": "Система контроля и управления доступом",
    "47-СС.СВДС": "Система видеодомофонной связи",
    "48-СС.СОТС": "Система охранной сигнализации",
    "49-НСС": "Наружные сети связи",
    "50-ОЗДС": "Охранно-защитная дератизационная система",
    "51-СС.СВН": "Система видеонаблюдения",
    "52-СПА": "Автоматическая пожарная сигнализация",
    "53-СОУЭ": "Система оповещения и управления эвакуацией",
    "54-АВТ": "Автоматизация инженерных систем",
    "55-АСУД": "Автоматизированная система управления и диспетчеризации",
    "56-ИТП.АТМ": "Индивидуальный тепловой пункт. Автоматизация",
    "57-ТХ1": "Технологические решения",
    "58-ВТ1": "Вертикальный транспорт. Лифт №1",
    "59-ВТ2": "Вертикальный транспорт. Лифт №2",
    "60-ТС.УУТЭ": "Тепловые сети. Узел учета тепловой энергии",
    "61-ОВ1.ЦОД": "Система вентиляции ЦОД",
    "62-ОВ2.ЦОД": "Система кондиционирования ЦОД",
    "63-АОВ.ЦОД": "Автоматизированная система управления вентиляцией ЦОД",
    "64-ЭОМ.ЦОД": "Силовое электрооборудование и освещение ЦОД",
    "65-СКК.ЦОД": "Система лотков и кабельных каналов ЦОД",
    "66-СКС.ЦОД": "Структурированная кабельная система ЦОД",
    "67-СКУД.ЦОД": "Система контроля и управления доступом ЦОД",
    "68-СОТ.ЦОД": "Система охранного телевидения ЦОД",
    "69-ФП.ЦОД": "Система фальшпола ЦОД",
    "70-АСУД.ЦОД": "Автоматизированная система диспетчеризации ЦОД",
    "71-АУГП.ЦОД": "Система автоматического газового пожаротушения ЦОД",
    "72-СПА.ЦОД": "Система пожарной автоматики ЦОД",
    "73-СРОП.ЦОД": "Система раннего обнаружения пожара ЦОД",
    "74-КЖ0.6": "Конструкции ограждений",
    "75-АР.НВФХМ": "Устройство навесного вентилируемого фасада",
    "76-ЭВКС": "Система защищенной видеоконференцсвязи"
}

class Document(models.Model):
    STAGE_CHOICES = [
        ('WORK', '✅ В производство работ (Штамп ПТО)'),
        ('REVIEW', '⏳ На проверке / Входной контроль'),
        ('ARCHIVED', '🚫 Аннулирован (Заменён новой ревизией)'),
    ]

    title = models.CharField(max_length=255, verbose_name="Наименование комплекта/тома")
    file = models.FileField(upload_to='pdfs/', verbose_name="Файл чертежа (PDF)")
    file_hash = models.CharField("SHA-256 отпечаток", max_length=64, blank=True, db_index=True)
    revision_num = models.PositiveIntegerField("Номер ревизии", default=1)
    work_status = models.CharField(
        "Статус допуска РД", max_length=20, choices=STAGE_CHOICES, default='WORK'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки в штаб")
    owner = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    null=True,
    blank=True,
    verbose_name="Владелец пространства (Компания)"
)

    class Meta:
        verbose_name = "Загруженный чертеж (PDF)"
        verbose_name_plural = "🪐 Склад чертежей Бронепоезда (PDF)"

    def __str__(self):
        return f"{self.title} [Рев. {self.revision_num}]"

    @property
    def get_status_icon(self) -> str:
        """Возвращает наглядный строительный штамп допуска для шаблонов."""
        icons = {
            'WORK': '✅ В производство работ',
            'REVIEW': '⏳ На проверке ПТО',
            'ARCHIVED': '🚫 АННУЛИРОВАН (Устарел)',
        }
        return icons.get(self.work_status, '📄 В работе')


class ParsedPage(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='pages', verbose_name="Документ")
    page_number = models.IntegerField(db_index=True, verbose_name="Номер страницы")
    text = models.TextField(verbose_name="Распознанный ИИ-текст")
    detected_axes = models.CharField(max_length=100, blank=True, default="", verbose_name="Вырезанные оси")
    detected_k_com = models.CharField(max_length=50, blank=True, default="", verbose_name="Коэффициент уплотнения")

    class Meta:
        ordering = ['document', 'page_number']
        unique_together = ('document', 'page_number')
        verbose_name = "Распознанная страница"
        verbose_name_plural = "📊 Кэш распознанных листов"

    def __str__(self):
        return f"{self.document.title} — лист {self.page_number}"

    def get_official_norm_name(self):
        """🧠 ТВОЙ СВЕРХЗРЯЧИЙ МНОГОССЫЛОЧНЫЙ МЕТОД"""
        found = [f"{code} ({desc})"
                 for code, desc in OFFICIAL_GOST_NORMS.items()
                 if code.lower() in self.text.lower()]
        if not found:
            return "Не определено по ГОСТ"
        if len(found) == 1:
            return found[0]
        return f"{found[0]} (+ {len(found) - 1} ссылок: {', '.join(found[1:3])})"

# 🔥 ЖЕЛЕЗОБЕТОННЫЙ ВЗВОД ТАБЛИЦЫ КАДРОВ, КОТОРУЮ ПОТЕРЯЛ ИМПОРТ VIEWS.PY
class ItrStaff(models.Model):

    ITR_ROLES = [
    ('CEO', '👑 Владелец / Директор (CEO)'),
    ('PTO', '📐 Инженер ПТО / Главный архитектор'),
    ('PRORAB', '👷 Начальник участка / Прораб / Мастер СМР'),
    ('SUPPLY', '🛒 Снабженец / Комплектатор (B2B)'),
    ('WAREHOUSE', '📦 Кладовщик / Завскладом'),
    ('ESTIMATOR', '💰 Сметчик / Инженер ОТиЗ'),
    ('SAFETY', '🦺 Инженер ОТ и ТБ (Охрана труда)'),
    ('GEODESY', '🧭 Геодезист / Лаборант стройконтроля'),
]

    staff_id = models.CharField(max_length=50, primary_key=True, verbose_name="Табельный номер")
    name = models.CharField(max_length=150, verbose_name="ФИО сотрудника")
    role_type = models.CharField(max_length=100, verbose_name="Должность")
    rate_per_shift = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name="Ставка за смену (руб)")
    owner = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    null=True,
    blank=True,
    verbose_name="Владелец пространства (Компания)"
)
    class Meta:
        verbose_name = "Инженер ИТР"
        verbose_name_plural = "🪪 Линейный состав ПТО (Кадры)"

    def __str__(self):
        return f"{self.name} ({self.role_type})"

class WarehouseTmc(models.Model):
    item_code = models.CharField(max_length=100, primary_key=True, verbose_name="Код материала по ГОСТ")
    nomenclature = models.CharField(max_length=255, verbose_name="Номенклатурное наименование")
    unit = models.CharField(max_length=50, default="ед.", verbose_name="Ед. изм.")
    stock_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, verbose_name="Остаток на складе")
    owner = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    null=True,
    blank=True,
    verbose_name="Владелец пространства (Компания)"
)
    class Meta:
        verbose_name = "Материал ТМЦ"
        verbose_name_plural = "🛒 Оперативные остатки ТМЦ (Склад)"

    def __str__(self):
        return f"{self.item_code} — {self.nomenclature}"

class TowerCrane(models.Model):
    """🏗️ БАШЕННЫЕ КРАНЫ И МЕХАНИЗАЦИЯ ОБЪЕКТА"""
    code = models.CharField("Инв. номер крана", max_length=30, unique=True)  # Напр. БК-1
    model_name = models.CharField("Марка крана", max_length=100)           # Напр. Liebherr 154 EC-H
    corpus = models.CharField("Зона обслуживания (Корпус)", max_length=50)
    max_load_tons = models.DecimalField("Грузоподъёмность (т)", max_digits=5, decimal_places=2, default=8.0)
    is_active = models.BooleanField("В работе", default=True)

    class Meta:
        verbose_name = "Башенный кран"
        verbose_name_plural = "🏗️ Башенные краны и техника"

    def __str__(self):
        return f"{self.code} ({self.model_name}) — {self.corpus}"


class WorkFront(models.Model):
    """🏢 ПАРАЛЛЕЛЬНЫЕ ПОТОКИ РАБОТ (КОРПУС / ЭТАЖ / БРИГАДА)"""
    corpus = models.CharField("Корпус / Секция", max_length=50, default="Корпус 1")
    floor_label = models.CharField("Этаж / Ярус", max_length=30)             # Напр. "1-25 этаж" или "5 этаж"
    axes_range = models.CharField("Диапазон осей", max_length=100)           # Напр. "Оси 1-36 / А-Я"
    brigade_type = models.CharField("Профиль бригады", max_length=100)       # Каменщики, Отделочники, Монолитчики
    work_name = models.CharField("Наименование работ", max_length=255)
    assigned_crane = models.ForeignKey(
    TowerCrane, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Привязанный кран"
    )
    progress_pct = models.PositiveIntegerField("Готовность (%)", default=0)

    class Meta:
        ordering = ['corpus', 'floor_label', 'brigade_type']
        verbose_name = "Фронт работ (Захватка)"
        verbose_name_plural = "🏢 Фронты работ по этажам и бригадам"

    def __str__(self):
        return f"{self.corpus} | {self.floor_label} | {self.brigade_type} — {self.work_name}"

class SectionDict(models.Model):
    code = models.CharField("Шифр", max_length=32, unique=True)
    section = models.CharField("Раздел РД", max_length=100)
    snip_ref = models.CharField("Нормативная ссылка", max_length=120, blank=True)
    snip_url = models.URLField("Ссылка на текст СП/ГОСТ", blank=True)

    class Meta:
        verbose_name = "Шифр раздела (Справочник)"
        verbose_name_plural = "Справочник шифров РД и СП"

    def __str__(self):
        return f"{self.code} — {self.section}"

class PurchaseRequest(models.Model):
    RECORD_TYPES = [
        ('BUY', '🛒 Закупка ТМЦ'),
        ('TEP', '📊 ТЭП (График ГПР/ННС)'),
        ('LIMIT', '⚠️ Допуск / Ограничение'),
    ]
    STATUS_CHOICES = [
        ('NEW', '🟡 Новая заявка'),
        ('IN_PROGRESS', '🔵 В закупке / Счёт'),
        ('PAID', '🟢 Оплачено'),
        ('DELIVERED', '✅ На складе / В монтаже'),
    ]

    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='purchase_requests')
    record_type = models.CharField("Категория", max_length=10, choices=RECORD_TYPES, default='BUY')
    discipline = models.CharField("Раздел РД", max_length=20, blank=True)
    floor_info = models.CharField("Этаж / Отметка", max_length=60, blank=True)
    room_info = models.CharField("Помещение", max_length=120, blank=True)
    node_cabinet = models.CharField("Шкаф / Узел / Пирог", max_length=120, blank=True)
    material_name = models.CharField("Наименование / Показатель", max_length=255)
    unit = models.CharField("Ед. изм.", max_length=32)
    required_qty = models.DecimalField("По проекту", max_digits=12, decimal_places=2, default=0)
    deficit_qty = models.DecimalField("К закупке", max_digits=12, decimal_places=2, default=0)
    responsible_itr = models.CharField("Ответственный", max_length=120, blank=True)
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='NEW')
    notes = models.CharField("Примечание", max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    brigade_assigned = models.CharField("Бригада / Исполнитель", max_length=120, blank=True)
    progress_pct = models.PositiveSmallIntegerField("Ход выполнения (%)", default=0)
    schedule_hint = models.CharField("График / Срок (смен)", max_length=80, blank=True)


    external_uid = models.UUIDField("API / HTTPS ключ", default=uuid.uuid4, editable=False, db_index=True)
    supplier_url = models.URLField("Ссылка на счёт / поставщика (HTTPS)", max_length=500, blank=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    @property
    def get_search_url(self) -> str:
        """Генерирует готовую HTTPS-ссылку для мгновенного поиска поставщика и цены."""
        if self.supplier_url:
            return self.supplier_url
        query = quote_plus(f"{self.material_name} купить цена")
        return f"https://yandex.ru{query}"


    class Meta:
        verbose_name = "Позиция спецификации / Заявка"
        verbose_name_plural = "🛒 Заявки, ТЭПы и Допуски ПТО"

    def __str__(self):
        return f"[{self.get_record_type_display()}] {self.material_name} ({self.deficit_qty} {self.unit})"

class BrigadeSafetyPass(models.Model):
    """Реестр подрядчиков, бригад, допусков ОТ и ТБ и журнал откликов на инструктаж."""
    HAZARD_CHOICES = [
        ('NONE', '🟢 Общестроительные работы (стандартный режим)'),
        ('HEIGHT', '⚠️ ВЫСОТА (> 1.8 м / леса / подмости / кровля)'),
        ('EXCAVATION', '⚠️ КОТЛОВАН / ТРАНШЕЯ (глубина > 1.5 м)'),
        ('ELECTRIC', '⚠️ ЭЛЕКТРОУСТАНОВКИ / ЩИТОВЫЕ (до/свыше 1000В)'),
        ('CRANE', '⚠️ ПОГРУЗОЧНО-РАЗГРУЗОЧНЫЕ / КРАНОВЫЕ РАБОТЫ'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Владелец")
    discipline = models.CharField("Раздел РД (КЖ, АР, СКС...)", max_length=32, default="КЖ")
    contractor_name = models.CharField("Подрядчик / Участок", max_length=160, default="Собственные силы (Участок №1)")
    brigadier_name = models.CharField("Бригадир / Ответственный", max_length=120)
    workers_count = models.PositiveSmallIntegerField("Численность бригады (чел.)", default=5)
    contact_channel = models.CharField("Контакт (Telegram ID / Телефон / Email)", max_length=120, blank=True)

    hazard_signal = models.CharField("Сигнал опасности ОТ и ТБ", max_length=20, choices=HAZARD_CHOICES, default='NONE')
    briefing_text = models.TextField("Текст целевого инструктажа", blank=True)

    # Цифровой отклик рабочего/бригадира и утверждение инженером ТБ
    worker_acknowledged = models.BooleanField("Отклик: Инструктаж прочитан и принят", default=False)
    acknowledged_at = models.DateTimeField("Время отклика в журнале ТБ", null=True, blank=True)
    safety_engineer_approved = models.BooleanField("Утверждено инженером ОТ и ТБ", default=False)

    # Фотоотчёт с площадки (СИЗ, ограждения, привязи)
    photo_report = models.ImageField("Фотоотчёт ТБ (СИЗ / Ограждения)", upload_to="safety_photos/%Y/%m/", blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    axes_from_to = models.CharField("Оси / Границы участка (Откуда → Куда)", max_length=120, blank=True)
    elevation_mark = models.CharField("Высотная отметка (Z)", max_length=60, blank=True)
    progress_pct = models.PositiveSmallIntegerField("Выполнение по фотоотчёту (%)", default=0)
    aosr_ready = models.BooleanField("АОСР выпущен (Финансовая броня)", default=False)
    supply_48h_ok = models.BooleanField("Материалы на 48ч обеспечены", default=True)


    class Meta:
        verbose_name = "Допуск бригады и журнал ОТ и ТБ"
        verbose_name_plural = "Реестр бригад и журнал ОТ и ТБ"

    def __str__(self):
        return f"[{self.discipline}] {self.contractor_name} ({self.workers_count} чел.)"

    @property
    def access_status_badge(self) -> str:
        if self.worker_acknowledged and self.safety_engineer_approved:
            return "🟢 ДОПУСК ОТ И ТБ УТВЕРЖДЁН"
        if self.worker_acknowledged:
            return "🟡 ПРОЧИТАНО (Ждёт утверждения ТБ)"
        return "🔴 НЕТ ОТКЛИКА ПО ИНСТРУКТАЖУ"


class PartnerVendorLead(models.Model):
    """B2B-радар заводов, поставщиков и их прайсов (для вкладки Снабжение и окна Инф())."""
    vendor_name = models.CharField("Поставщик / Завод", max_length=150)
    contact_email = models.EmailField("E-mail поставщика", blank=True)
    website_url = models.URLField("Сайт / Каталог", blank=True)
    category_group = models.CharField("Категория ТМЦ", max_length=100, default="Общестроительные ТМЦ")
    region = models.CharField("Регион поставки", max_length=100, default="г. Тула / ЦФО")
    source_document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="vendor_leads")
    source_page = models.PositiveIntegerField("Лист РД", default=1)
    project_materials = models.TextField("Заложенные позиции и объёмы из РД", blank=True)
    unit_price_rub = models.DecimalField("Ориентир цены (₽ с НДС)", max_digits=12, decimal_places=2, default=0)
    status = models.CharField(
        "Статус B2B",
        max_length=20,
        choices=[
            ("NEW", "Новый лид из РД"),
            ("INVITED", "Запрос счёта отправлен"),
            ("PARTNER", "Аккредитованный партнёр"),
        ],
        default="NEW",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "B2B-поставщик из проекта"
        verbose_name_plural = "B2B-радар поставщиков"
        unique_together = ("vendor_name", "contact_email", "source_document")

    def __str__(self):
        return f"{self.vendor_name} ({self.region})"


class BimCrossLink(models.Model):
    """Сквозная инженерная связь узлов, объёмов и коллизий между всеми 76 томами РД, Складом и АОСР."""

    DISCIPLINE_CHOICES = [
        ("GP", "ГП (Генплан и сети)"),
        ("AR", "АР / АИ (Архитектура и отделка)"),
        ("KJ", "КЖ / КМ (Конструктив и фундаменты)"),
        ("ES", "ЭС / ЭОМ (Электроснабжение)"),
        ("OV", "ОВиК / ИТП (Отопление, вентиляция, холод)"),
        ("VK", "ВК / НВК (Водопровод и канализация)"),
        ("SS", "АСУ ТП / СС (Автоматика и связь)"),
        ("WH", "Склад ТМЦ и логистика"),
    ]

    STATUS_CHOICES = [
        ("MATCHED", "✅ Подтверждено в смежном томе и на складе"),
        ("COLLISION", "⚠️ Коллизия / Нет закладной / Расхождение объёмов"),
        ("RFI_SENT", "📨 Отправлен вопрос проектировщику (Авторский надзор)"),
        ("RESOLVED", "🟢 Устранено / Согласовано ПТО"),
        ("INFO", "ℹ️ Справочная привязка по осям"),
    ]

    bim_tag = models.CharField("Сквозной BIM-тег (марка / узел / ввод)", max_length=120, db_index=True)
    axes_and_elevation = models.CharField("Оси, помещение и отметка", max_length=120, blank=True)

    source_discipline = models.CharField("Раздел-источник", max_length=10, choices=DISCIPLINE_CHOICES, default="GP")
    source_document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="outgoing_bim_links")
    source_page = models.PositiveIntegerField("Лист источника", default=1)
    source_qty = models.DecimalField("Объём в источнике", max_digits=12, decimal_places=2, default=0)

    target_discipline = models.CharField("Смежный раздел / Контур", max_length=10, choices=DISCIPLINE_CHOICES, default="KJ")
    target_document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name="incoming_bim_links", null=True, blank=True
    )
    target_page = models.PositiveIntegerField("Связанный лист", null=True, blank=True)
    target_qty = models.DecimalField("Объём в смежном томе", max_digits=12, decimal_places=2, default=0)
    warehouse_qty = models.DecimalField("Остаток на складе ТМЦ", max_digits=12, decimal_places=2, default=0)

    purchase_request = models.ForeignKey(
        "PurchaseRequest", on_delete=models.SET_NULL, null=True, blank=True, related_name="bim_links",
        verbose_name="Связанная заявка на закупку"
    )

    link_status = models.CharField("Статус инженерной сверки", max_length=20, choices=STATUS_CHOICES, default="INFO")
    engineering_note = models.TextField("Инженерный вывод и рекомендации ПТО", blank=True)
    assigned_to = models.CharField("Ответственный (ГИП / ИТР / Снабжение)", max_length=120, default="ПТО Штаб")
    resolved_at = models.DateTimeField("Дата снятия коллизии", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Сквозная BIM-связь РД"
        verbose_name_plural = "Сквозные BIM-связи РД"
        ordering = ["-created_at"]

    @property
    def qty_delta(self):
        return self.source_qty - self.target_qty

    def __str__(self):
        return f"{self.bim_tag} ({self.source_discipline} ↔ {self.target_discipline}) [{self.get_link_status_display()}]"
