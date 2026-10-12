from django.db import models
from django.contrib.auth.models import User

class ITRMember(models.Model):
    """Полная инженерно-техническая структура строительной площадки"""
    ROLES = [
        # Линейное руководство и управление участками
        ("CHIEF_ENG", "Главный инженер проекта / Нач. объекта"),
        ("SITE_CHIEF", "Начальник строительного участка"),
        ("FOREMAN", "Производитель работ (Прораб)"),
        ("MASTER", "Мастер строительно-монтажных работ"),
        
        # Инженерно-технические службы (ПТО и Сметы)
        ("PTO_CHIEF", "Начальник производственно-технического отдела"),
        ("PTO_ENG", "Инженер ПТО (Ведение ИД, Чертежи)"),
        ("ESTIMATOR", "Инженер-сметчик (Учет стоимости, КС-2/КС-3)"),
        
        # Специализированный ИТР-состав площадки
        ("GEODESIST", "Инженер-геодезист (Оси, Разбивочные работы)"),
        ("ENERGY_ENG", "Главный энергетик (Силовые сети, ЭОМ)"),
        ("MECH_ENG", "Главный механик (Строительные машины, КМ)"),
        ("QA_ENG", "Инженер контроля качества (Строительный контроль)"),
        ("BIM_COORD", "Специалист информационного моделирования (BIM/IFC)"),
        ("HSE_ENG", "Специалист по охране труда и промбезопасности"),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="itr_profile")
    role = models.CharField(max_length=20, choices=ROLES, verbose_name="ИТР Должность")
    telegram_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="ID связи (Telegram)")
    is_active_on_site = models.BooleanField(default=True, verbose_name="Находится на площадке")

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} [{self.get_role_display()}]"

class DXFBlueprintLayer(models.Model):
    """Векторные слои CAD/BIM для совместной работы всего ИТР-состава"""
    blueprint_name = models.CharField(max_length=255, verbose_name="Имя файла чертежа")
    layer_name = models.CharField(max_length=100, verbose_name="Имя CAD-слоя (Шифр)")
    detected_materials = models.JSONField(verbose_name="Физические объемы (ИИ-Парсинг)")
    verified_by = models.ForeignKey(ITRMember, on_delete=models.SET_NULL, null=True, blank=True, related_name="verified_layers")
    status_notes = models.TextField(blank=True, null=True, verbose_name="Замечания технадзора / ПТО")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.blueprint_name} -> {self.layer_name}"
