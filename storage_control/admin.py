# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import VideoCapsule, BloggerUsage, FamilyLegacy, NetworkIncident, ConstructionCompany

# Меняем стандартные заголовки Django на премиальный b2b-стиль холдинга FAMILYMIRO 1.6
admin.site.site_header = "🦅 FAMILYMIRO 1.6 — Главный Командный Мостик холдинга"
admin.site.site_title = "Панель Генерального Конструктора Макса Косарева"
admin.site.index_title = "📊 Сводный Аналитический Монитор Данных и Капитала"

@admin.register(FamilyLegacy)
class FamilyLegacyAdmin(admin.ModelAdmin):
    list_display = ('entity_name', 'record_type', 'timestamp')
    list_filter = ('record_type',)
    search_fields = ('entity_name', 'text_content')

@admin.register(NetworkIncident)
class NetworkIncidentAdmin(admin.ModelAdmin):
    list_display = ('user_ip', 'country', 'detected_intent', 'timestamp')
    list_filter = ('country',)
    search_fields = ('user_ip', 'detected_intent')

@admin.register(BloggerUsage)
class BloggerUsageAdmin(admin.ModelAdmin):
    list_display = ('blogger_name', 'daily_limit', 'accumulated_income')

@admin.register(VideoCapsule)
class VideoCapsuleAdmin(admin.ModelAdmin):
    list_display = ('video_title', 'is_public')

@admin.register(ConstructionCompany)
class ConstructionCompanyAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'total_budget')
