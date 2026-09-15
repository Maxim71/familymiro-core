from django.apps import AppConfig

class StorageControlConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'  # Добавьте эту строку
    name = 'storage_control'
