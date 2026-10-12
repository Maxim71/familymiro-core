from django.contrib import admin
from .models import ITRMember, PartnerPin, StoreOrder, GuestMediaLog

@admin.register(ITRMember)
class ITRMemberAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "balance_rub", "telegram_id")
    list_filter = ("role",)
    search_fields = ("user__username", "telegram_id")

@admin.register(PartnerPin)
class PartnerPinAdmin(admin.ModelAdmin):
    list_display = ("title", "code", "price_rub", "discount_value")
    search_fields = ("title", "code")

@admin.register(StoreOrder)
class StoreOrderAdmin(admin.ModelAdmin):
    list_display = ("id", "buyer", "pin_item", "ordered_at", "is_paid")
    list_filter = ("is_paid", "ordered_at")
    search_fields = ("buyer__user__username", "pin_item__code")

@admin.register(GuestMediaLog)
class GuestMediaLogAdmin(admin.ModelAdmin):
    list_display = ("session_key", "watched_trend", "seo_source", "entered_at")
    list_filter = ("seo_source", "entered_at")
