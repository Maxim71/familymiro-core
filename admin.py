from django.contrib import admin
from .models import Agreement, VideoCapsule, AvatarEzhik, InteractiveComment, PunchListItem, BloggerUsage

from django.utils.safestring import mark_safe
from .models import ConstructionObject

@admin.register(Agreement)
class AgreementAdmin(admin.ModelAdmin):
    """
    [Сейф Наследия — Выпрямленная Админка]
    """
    # Исправлено на capsule_id, category, unlock_date строго по ДНК вашей модели!
    list_display = ('capsule_id', 'category', 'unlock_date', 'is_public', 'is_approved_by_ezhik', 'created_at')
    list_filter = ('category', 'is_public', 'is_approved_by_ezhik', 'created_at')
    search_fields = ('capsule_id', 'receiver_email', 'receiver_phone', 'seo_slug')
    prepopulated_fields = {'seo_slug': ('capsule_id',)}


@admin.register(VideoCapsule)
class VideoCapsuleAdmin(admin.ModelAdmin):
    """
    [Капсулы видео для блогеров]
    """
    list_display = ('agreement', 'file_path', 'is_processed_by_director', 'uploaded_at')
    list_filter = ('is_processed_by_director',)


@admin.register(AvatarEzhik)
class AvatarEzhikAdmin(admin.ModelAdmin):
    """
    [Капитал и ИИ-Интеллект Ёжика]
    """
    list_display = ('name', 'total_revenue', 'is_learning', 'updated_at')


@admin.register(InteractiveComment)
class InteractiveCommentAdmin(admin.ModelAdmin):
    """
    [Лингвистический контур комментариев]
    """
    list_display = ('author_name', 'blog_type', 'is_approved_by_ezhik', 'created_at')
    list_filter = ('blog_type', 'is_approved_by_ezhik')


@admin.register(PunchListItem)
class PunchListItemAdmin(admin.ModelAdmin):
    """
    [Технадзор: Контроль строительной площадки]
    """
    list_display = ('building_block', 'floor', 'room', 'axis', 'is_closed', 'approved_by_author')
    list_filter = ('building_block', 'floor', 'is_closed', 'approved_by_author')
    search_fields = ('room', 'axis', 'description', 'assigned_to')


@admin.register(BloggerUsage)
class BloggerUsageAdmin(admin.ModelAdmin):
    """
    [Контур Скорости: Жесткие лимиты 12 медиа/день]
    """
    list_display = ('username', 'photo_video_count', 'last_upload_date')


# Красивое кастомное оформление шапки админки (Пульт Капитана)
admin.site.site_header = "🦔 FAMILYMIRO 1.6 — ПУЛЬТ УПРАВЛЕНИЯ КАПИТАЛОМ ОТЦА"
admin.site.site_title = "Архитектор: Максим Косарев"
admin.site.index_title = "Центральный суверенный контур аналитики"

@admin.register(InteractiveComment)
class InteractiveCommentAdmin(admin.ModelAdmin):
    """Модерация Глобального Эфира Ёжика"""
    list_display = ('id', 'author_name', 'blog_type', 'is_approved_by_ezhik', 'created_at')
    list_filter = ('is_approved_by_ezhik', 'blog_type', 'created_at')
    search_fields = ('author_name',)
    list_editable = ('is_approved_by_ezhik',) # Можно одобрять весточки прямо из списка!
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(is_approved_by_ezhik=True)
    approve_comments.short_description = "🟢 Пропустить выбранные потоки в Эфир"

@admin.register(Agreement)
class AgreementAdmin(admin.ModelAdmin):
    """Вековой Сейф и Уговоры Рода"""
    list_display = ('capsule_id', 'receiver_email', 'teaser_video_path')
    search_fields = ('capsule_id',)

@admin.register(PunchListItem)
class PunchListItemAdmin(admin.ModelAdmin):
    """Пульт строительного контроля по ГОСТ 475-2016"""
    list_display = ('id', 'is_closed')
    list_filter = ('is_closed',)
    list_editable = ('is_closed',)

@admin.register(BloggerUsage)
class BloggerUsageAdmin(admin.ModelAdmin):
    """Аналитика трафика и лимитов Блогеров"""
    list_display = ('username', 'action', 'timestamp')
    list_filter = ('username', 'timestamp')

admin.site.site_heаder = "КОВЧЕГ MIROHA.RU"
admin.site.site_title = "Панель - Архитектора"
admin.site.index_title = "Упровлене Вековыми Выгрузками"

@admin.register(ConstructionObject)
class ConstructionObjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'country', 'object_capital', 'currency', 'created_at')
    list_filter = ('city', 'country', 'created_at')
    search_fields = ('name', 'city', 'address')
    
    # Прямоугольная обтекаемая MOBA-кнопка запуска Робота-Ёжика по всей России
    readonly_fields = ('ezhik_parser_console',)
    
    def ezhik_parser_console(self, obj):
        return mark_safe('''
            <div style="background: rgba(13, 27, 42, 0.9); border: 2px solid #00f0ff; border-radius: 16px; padding: 20px; box-shadow: 0 0 15px rgba(0, 240, 255, 0.2); max-width: 400px;">
                <h4 style="color: #00f0ff; margin: 0 0 10px 0; font-family: monospace; text-transform: uppercase;">📡 Всероссийский ИИ-Парсер Реестров</h4>
                <form method="POST" action="/api/federal-parse/">
                    <input type="hidden" name="csrfmiddlewaretoken" value="'''+'''+'''">
                    <label style="color: #8b949e; font-size: 11px; display: block; margin-bottom: 5px;">ПЛАНОВЫЙ ГОД ЗАСТРОЙКИ:</label>
                    <select name="year" style="width: 100%; background: #161b22; color: #fff; border: 1px solid #30363d; padding: 5px; margin-bottom: 10px;">
                        <option value="2026">Текущий 2026 год</option>
                        <option value="2027">Запланированный 2027 год</option>
                        <option value="2028">Ближайшие до 2030 года</option>
                    </select>
                    <button type="submit" style="width: 100%; background: linear-gradient(90deg, #00f0ff 0%, #0077ff 100%); border: none; border-radius: 12px; color: #fff; padding: 10px; font-weight: bold; cursor: pointer; text-transform: uppercase; font-size: 11px; letter-spacing: 1px;">
                        ⚡ Запустить Охотника по России
                    </button>
                </form>
            </div>
        ''')
    ezhik_parser_console.short_description = "Капитанский пульт Робота-Ёжика"
