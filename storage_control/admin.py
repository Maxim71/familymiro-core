# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.html import format_html
from .models import VideoCapsule, ConstructionCompany, NetworkIncident, MezaninProduct

@admin.register(MezaninProduct)
class MezaninProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'source_platform', 'base_price', 'margin_percent', 'final_price_display', 'product_image_preview')
    list_filter = ('source_platform', 'is_available')
    search_fields = ('title',)

    def final_price_display(self, obj):
        return format_html('<b style="color: #10b981; font-family: monospace;">{} ₽</b>', obj.final_price)
    final_price_display.short_description = "Цена с маржой"

    def product_image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; aspect-ratio: 4/3; object-fit: cover; border-radius: 4px; border: 1px solid #1a73e8;" />', obj.image.url)
        return format_html('<span style="color: #64748b; font-size: 0.75rem;">Нет фото</span>')
    product_image_preview.short_description = "Превью"

@admin.register(NetworkIncident)
class NetworkIncidentAdmin(admin.ModelAdmin):
    list_display = ('id', 'kill_switch_status')
    def kill_switch_status(self, obj):
        return format_html('<span style="color: #10b981; font-weight: bold;">🟢 WORKERS ACTIVE</span>')

@admin.register(VideoCapsule)
class VideoCapsuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'video_verification_player')
    def video_verification_player(self, obj):
        return format_html('<div style="width: 60px; height: 35px; background: #000;"></div>')

@admin.register(ConstructionCompany)
class ConstructionCompanyAdmin(admin.ModelAdmin):
    list_display = ('id',)
