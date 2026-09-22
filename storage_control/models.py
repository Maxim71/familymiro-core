from django.db import models

class UserMaskProfile(models.Model):
    """👥 МАТРИЦА МАСОК МАКСИМА (Multi-Role Management Core)"""
    client_id = models.CharField("ИТР Код Client ID", max_length=50, unique=True, help_text="Напр: CID-PRO-MIHALYCH")
    active_role = models.CharField("Активная Маска / Роль", max_length=100, help_text="Администратор, ПТО, Разнорабочий, Отец для вечности и т.д.")
    phone_number = models.CharField("Номер телефона для связи", max_length=30, blank=True, null=True)
    google_totp_secret = models.CharField("Криптографический КЛЮЧ-ТОННЕЛЬ (Base32)", max_length=64, blank=True, null=True)
    created_at = models.DateTimeField("Дата фиксации в вечности", auto_now_add=True)

    class Meta:
        verbose_name = "Маска Максима / Профиль Пользователя"
        verbose_name_plural = "👥 1. Матрица Масок и Профилей"

    def __str__(self):
        return f"{self.client_id} — [{self.active_role}]"


class SoftwareLicense(models.Model):
    """📜 СУБД-КОНТУР ЛИЦЕНЗИРОВАНИЯ ПО (Защита от нелегального клика)"""
    STATUS_CHOICES = [('ACTIVE', 'АКТИВНА // Secured'), ('EXPIRED', 'ИСТЕКЛА // Blocked')]
    
    profile = models.ForeignKey(UserMaskProfile, on_delete=models.CASCADE, verbose_name="Привязка к Профилю")
    license_key = models.CharField("Ключ Лицензии ПО", max_length=100, unique=True, help_text="Напр: MIRO-MASTER-BOSS-2026")
    license_type = models.CharField("Пакет / Тип Лицензии", max_length=100, help_text="Линейная ИТР, Полный Мезонин, Благотворительная")
    status = models.CharField("Статус Лицензии в Postgres", max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    expires_at = models.DateField("Срок действия Лицензии")

    class Meta:
        verbose_name = "Коммерческая Лицензия ПО"
        verbose_name_plural = "📜 2. Контур Лицензирования ПО"

    def __str__(self):
        return f"{self.license_key} ({self.status})"


class MezaninWebsiteBuilder(models.Model):
    """🛒 КОНСТРУКТОР САЙТОВ-МЕЗОНИНОВ (Сайты-визитки, Чат-боты, Блоги Многие-ко-Многим)"""
    SITE_TYPES = [('BLOG', 'Блог ИТР-Монологов'), ('VCARD', 'Сайт-Визитка СРО'), ('CHATBOT', 'Интерфейс Чат-Бота')]
    
    owner = models.ForeignKey(UserMaskProfile, on_delete=models.CASCADE, verbose_name="Создатель / Администратор")
    site_title = models.CharField("Название Сайта / Проекта", max_length=200)
    site_domain = models.CharField("Технический Домен / Туннель", max_length=100, help_text="Напр: blog.miroha.ru")
    architecture_type = models.CharField("Тип Конструктора Мезонина", max_length=20, choices=SITE_TYPES, default='BLOG')
    is_active = models.BooleanField("Запустить в полный ОЗУ-эфир Nginx?", default=True)

    class Meta:
        verbose_name = "Сайт Конструктора Мезонина"
        verbose_name_plural = "💻 3. Конструктор Сайтов и Блогов"

    def __str__(self):
        return f"{self.site_title} ({self.site_domain})"


class ArchivalDirective(models.Model):
    """💾 ДИРЕКТИВЫ АРХИВА ВЕЧНОСТИ (_proglog / decorator / frozenlist)"""
    associated_site = models.ForeignKey(MezaninWebsiteBuilder, on_delete=models.CASCADE, verbose_name="Связанный Проект")
    log_title = models.CharField("Заголовок Статьи / Монолога / Лога", max_length=200)
    log_content = models.TextField("Тело Монолога / Содержимое Директивы")
    media_file_path = models.CharField("Путь к загруженному Медиа (Фото/Видео/Аватарка)", max_length=255, blank=True, null=True, help_text="Обработка через imageio/moviepy/pillow")
    captured_timestamp = models.DateTimeField("Временная метка Вечности", auto_now_add=True)

    class Meta:
        verbose_name = "Директива Архива / Монолог"
        verbose_name_plural = "💾 4. Директивы Архива и Монологи"

    def __str__(self):
        return f"[{self.captured_timestamp.strftime('%d.%m %H:%M')}] {self.log_title}"
