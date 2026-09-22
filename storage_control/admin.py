from django.contrib import admin
from .models import UserMaskProfile, SoftwareLicense, MezaninWebsiteBuilder, ArchivalDirective

# Настройка глобальных ИТР-заголовков панели управления Максима
admin.site.site_header = "👑 MIROHA>ADMIN_PANEL_MAX"
admin.site.site_title = "Miroha Max Admin Panel"
admin.site.index_title = "Управление Монолитом Мезонина // Самозанятый ИТР-Контур"

@admin.register(UserMaskProfile)
class UserMaskProfileAdmin(admin.ModelAdmin):
    list_display = ('client_id', 'active_role', 'phone_number', 'created_at')
    search_fields = ('client_id', 'active_role')
    list_filter = ('active_role', 'created_at')

@admin.register(SoftwareLicense)
class SoftwareLicenseAdmin(admin.ModelAdmin):
    list_display = ('license_key', 'profile', 'license_type', 'status', 'expires_at')
    list_filter = ('status', 'license_type', 'expires_at')
    search_fields = ('license_key', 'license_type')
    list_editable = ('status',)

@admin.register(MezaninWebsiteBuilder)
class MezaninWebsiteBuilderAdmin(admin.ModelAdmin):
    list_display = ('site_title', 'owner', 'site_domain', 'architecture_type', 'is_active')
    list_filter = ('architecture_type', 'is_active')
    search_fields = ('site_title', 'site_domain')
    list_editable = ('is_active',)

@admin.register(ArchivalDirective)
class ArchivalDirectiveAdmin(admin.ModelAdmin):
    list_display = ('log_title', 'associated_site', 'media_file_path', 'captured_timestamp')
    search_fields = ('log_title', 'log_content')
    list_filter = ('captured_timestamp',)
