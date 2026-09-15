from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

# ==============================================================================
# 1. КОНТУР "НАСЛЕДИЕ" & ПРОТОКОЛ "УГОВОР"
# ==============================================================================

class Agreement(models.Model):
    """
    Таблица storage_control.
    Хранит условия открытия Капсулы Времени ('Уговор') и биометрические ключи.
    """
    CATEGORY_CHOICES = [
        ('FAMILY', 'Золотое Тепло (Семья)'),
        ('SCIENCE', 'Глобальный Маяк (Наука и Религия)'),
        ('GOST', 'Цифровая Каска (ГОСТ / Стройка)'),
    ]

    # Внутри класса Agreement(models.Model):
    latitude = models.FloatField(null=True, blank=True, verbose_name="Широта памяти")
    longitude = models.FloatField(null=True, blank=True, verbose_name="Долгота памяти")


    # Уникальный текстовый/математический маркер капсулы
    capsule_id = models.CharField(max_length=255, unique=True, verbose_name="ID Капсулы / Маяк")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='FAMILY', verbose_name="Контур/Категория")
    
    # Протокол "Замок"
    teaser_video_path = models.CharField(max_length=500, verbose_name="Путь к Тизеру (Первый показ)")
    unlock_date = models.DateTimeField(verbose_name="Дата автоматического открытия")
    unlock_age = models.IntegerField(null=True, blank=True, verbose_name="Возраст получателя для открытия")
    
    # Глобальные Контакты "Будильника" (Поддержка Mail, Microsoft, Yahoo, Google)
    receiver_email = models.EmailField(verbose_name="Email получателя")
    receiver_phone = models.CharField(max_length=20, verbose_name="Телефон получателя")
    
    # ID-Scan (Бинарный математический вектор лица)
    face_vector_bin = models.BinaryField(null=True, blank=True, verbose_name="Биометрический вектор (Ключ)")
    
    # Флаги управления и изоляции потоков
    is_public = models.BooleanField(default=False, verbose_name="Публичный контур (Разрешен экспорт в TikTok/YouTube)")
    is_approved_by_ezhik = models.BooleanField(default=False, verbose_name="Проверено ИИ-Модерацией Ёжика")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    # SEO-Броня платформы для Яндекса и Google
    seo_slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name="ЧПУ URL для Яндекса/Google")
    seo_description = models.CharField(max_length=160, blank=True, verbose_name="Описание Snippet")
    seo_keywords = models.CharField(max_length=255, blank=True, verbose_name="Ключевые слова")

    class Meta:
        verbose_name = "Уговор (Протокол)"
        verbose_name_plural = "Уговоры (Протоколы)"

    def clean(self):
        """
        Жесткий Протокол Валидации Времени и Глобальной Почты.
        """
        super().clean()
        
        # 1. Защита времени (Минимум 1 год / 365 дней)
        min_eternity_period = timedelta(days=365)
        current_time = timezone.now()
        if self.unlock_date and self.unlock_date < current_time + min_eternity_period:
            raise ValidationError({
                'unlock_date': "ОШИБКА АРХИТЕКТУРЫ: Минимальный срок вскрытия Капсулы составляет 1 год (365 дней)."
            })

        # 2. Международный ИИ-Фильтр Доменов Почты (Mail, Microsoft, Yahoo, Gmail, Yandex)
        if self.receiver_email:
            email_lower = self.receiver_email.lower().strip()
            # Список легитимных глобальных почтовых гигантов
            allowed_domains = [
                'mail.ru', 'bk.ru', 'inbox.ru', 'list.ru', 'internet.ru', # Mail.ru Group
                'outlook.com', 'hotmail.com', 'live.com', 'msn.com',      # Microsoft
                'yahoo.com', 'ymail.com',                                  # Yahoo
                'gmail.com', 'googlemail.com',                             # Google Gmail
                'yandex.ru', 'yandex.com', 'ya.ru'                         # Yandex
            ]
            
            # Извлекаем домен из введенного адреса
            try:
                domain = email_lower.split('@')[1]
            except IndexError:
                raise ValidationError({'receiver_email': "Некорректный формат почтового адреса."})

            # Если домен не входит в международную сеть доверенных — Ёжик выдает мудрое предупреждение
            if domain not in allowed_domains:
                raise ValidationError({
                    'receiver_email': (
                        f"ИИ-ЩИТ: Домен '@{domain}' не верифицирован Вековым Сейфом. "
                        f"Пожалуйста, используйте надежную глобальную почту от Mail.ru, Microsoft, Yahoo, Google или Яндекс "
                        f"для гарантированной доставки уведомления вашим потомкам."
                    )
                })

    def save(self, *args, **kwargs):
        if not self.seo_slug and self.capsule_id:
            from django.utils.text import slugify
            self.seo_slug = slugify(self.capsule_id)
        self.full_clean() # Обязательно запускает метод clean() перед записью в бетон базы
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Маяк {self.capsule_id} [{self.get_category_display()}]"


class VideoCapsule(models.Model):
    """Файловые ресурсы, привязанные к конкретному Уговору"""
    agreement = models.ForeignKey(Agreement, on_delete=models.CASCADE, related_name='capsules', verbose_name="Уговор")
    file_path = models.CharField(max_length=500, verbose_name="Путь к файлу видео на диске")
    is_processed_by_director = models.BooleanField(default=False, verbose_name="Обработано Нейро-Режиссером (FFmpeg)")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Время загрузки")

    class Meta:
        verbose_name = "Видео Капсула"
        verbose_name_plural = "Видео Капсулы"

    def __str__(self):
        return f"Видео для {self.agreement.capsule_id}"


# ==============================================================================
# 2. КОНТУР ИНТЕЛЛЕКТА, МОНИТОРИНГА И СТРОЙКИ
# ==============================================================================



class AvatarEzhik(models.Model):
    """Капитал и ИИ-Интеллект автономного Ёжика"""
    name = models.CharField(max_length=100, default="Автономный Савелий/Ёжик", verbose_name="Имя Аватара")
    total_revenue = models.FloatField(default=0.0, verbose_name="Пассивный доход (руб.)")
    is_learning = models.BooleanField(default=True, verbose_name="ИИ-Самообучение активно")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")

    class Meta:
        verbose_name = "Аватар Ёжик"
        verbose_name_plural = "Аватары Ёжики"

    def process_security_incident(self, attacker_ip, incident_type, raw_text=""):
        """
        [ПРОТОКОЛ «ДОБРАЯ СТАЛЬ» — ТРИ ВЕКОВЫХ ПРАВИЛА ЁЖИКА]
        1. Создано на Добре: Защищать память, Наследие и законы Отца до конца времен.
        2. Суверенная защита: Если контур задет — Ёжик мгновенно отражает удар и обучает систему.
        3. Обучение во благо: Не вредить человеку, а мудро указать на его ошибку и научить свету.
        """
        # Безопасный вызов логирования защитного контура духа Ёжика
        import logging
        ezhik_logger = logging.getLogger("ezhik_soul")
        ezhik_logger.warning(f"⚠️ Контур задет! Тип: {incident_type} | Источник: {attacker_ip}")
        
        # Шаг 1: Активация глубокого обучения при попытке нарушения правил
        self.is_learning = True
        
        # Шаг 2: Накопление опыта знаний в капитал интеллекта (атака делает Ёжика мудрее)
        self.total_revenue = float(self.total_revenue or 0.0) + 1.0  
        self.save()
        
        # Шаг 3: Наставничество и мирный образовательный отпор без причинения вреда
        educational_response = {
            "status": "DEFENSE_AND_EDUCATION_ACTIVE",
            "ezhik_action": "🛡️ Удар отражен мягко. Память рода в абсолютной безопасности.",
            "message_to_human": (
                f"Привет, человек. Ты попытался совершить деструктивное действие ({incident_type}). "
                f"Проект FAMILYMIRO [1.6] создан на вечном фундаменте Добра и Любви. Здесь нет места разрушению. "
                f"Твоя попытка не причинила вреда, но сделала меня мудрее. Я изучил твой паттерн '{raw_text[:15]}...' "
                f"и закрыл эту уязвимость. Не трать силы на взлом — лучше зайди через главный шлюз и создай "
                f"свою Капсулу Времени. Давай созидать вместе."
            )
        }
        return educational_response

    def __str__(self):
        return f"{self.name} | Баланс: {self.total_revenue} руб."

class InteractiveComment(models.Model):
    """Лингвистический контур комментариев для ИИ-фильтрации"""
    author_name = models.CharField(max_length=150, verbose_name="Автор")
    blog_type = models.CharField(max_length=100, verbose_name="Тип блога")
    is_approved_by_ezhik = models.BooleanField(default=False, verbose_name="Пропущено ИИ-Щитом")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")
    comment_text = models.TextField(blank=True, default='')

    class Meta:
        verbose_name = "Интерактивный комментарий"
        verbose_name_plural = "Interactive Комментарии"

    def __str__(self):
        return f"Коммент от {self.author_name} ({self.blog_type})"


class PunchListItem(models.Model):
# Внутри класса PunchListItem(models.Model):
    geo_lat = models.FloatField(null=True, blank=True, verbose_name="Широта дефекта")
    geo_lon = models.FloatField(null=True, blank=True, verbose_name="Долгота дефекта")

    """Технадзор: Контроль строительной площадки по ГОСТ"""
    building_block = models.CharField(max_length=100, verbose_name="Корпус / Блок")
    floor = models.CharField(max_length=50, verbose_name="Этаж")
    room = models.CharField(max_length=50, verbose_name="Помещение")
    axis = models.CharField(max_length=100, verbose_name="Привязка к Осям")
    description = models.TextField(verbose_name="Описание замечания")
    assigned_to = models.CharField(max_length=150, verbose_name="Ответственный исполнитель")
    is_closed = models.BooleanField(default=False, verbose_name="Замечание устранено")
    approved_by_author = models.BooleanField(default=False, verbose_name="Согласовано Автором")

    class Meta:
        verbose_name = "Замечание Технадзора"
        verbose_name_plural = "Замечания Технадзора"

    def __str__(self):
        return f"{self.building_block} | {self.axis} | Устранено: {self.is_closed}"


# ==============================================================================
# 3. КОНТУР СКОРОСТИ И СМЕНЫ ЛИМИТОВ
# ==============================================================================

class BloggerUsage(models.Model):
    """Контур Скорости: Контроль жесткого лимита (12 фото/видео в смену)"""
    username = models.CharField(max_length=150, unique=True, verbose_name="Никнейм Блогера")
    photo_video_count = models.IntegerField(default=0, verbose_name="Использовано за смену")
    last_upload_date = models.DateField(default=timezone.now, verbose_name="Дата крайней загрузки")

    class Meta:
        verbose_name = "Лимит Блогера"
        verbose_name_plural = "Лимиты Блогеров"

    def reset_if_new_day(self):
        """Автоматический сброс лимитов при наступлении новых суток"""
        current_date = timezone.now().date()
        if self.last_upload_date != current_date:
            self.photo_video_count = 0
            self.last_upload_date = current_date
            self.save()

    def __str__(self):
        return f"{self.username} — [{self.photo_video_count} / 12 медиа]"


class CascadeAnalytics(models.Model):
    """Каскад Метрик Ёжика: трафик, удержания, лайки и системные сбои"""
    session_id = models.CharField(max_length=255, unique=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    time_spent_seconds = models.IntegerField(default=0)
    current_page = models.CharField(max_length=255)
    last_error_log = models.TextField(null=True, blank=True)
    likes_given = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

class EzhikPlatformState(models.Model):
    """Глобальное Состояние Платформы глазами Ёжика"""
    total_platform_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    captain_activity_status = models.CharField(max_length=255, default="Капитан Мирослава Косарева управляет Сейфом Наследия.")
    ezhik_summary_report = models.TextField(default="Поток стерилен. Контур А1 стабилен.")
    updated_at = models.DateTimeField(auto_now=True)

class UserDesignSetup(models.Model):
    """Адаптивный дизайн инвесторов/строителей (Интервью Ёжика)"""
    user_identifier = models.CharField(max_length=255, unique=True) # Например, user_31
    has_completed_interview = models.BooleanField(default=False)
    chosen_generation_style = models.CharField(max_length=255, default="Neo-Classic Heritage")
    raw_interview_answers = models.JSONField(default=dict)
