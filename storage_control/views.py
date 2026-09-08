# -*- coding: utf-8 -*-
import os
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from .models import MezaninProduct

def index_family(request):
    return render(request, "storage_control/portal.html", {"captain": "Miroslava_Kosareva"})

def show_products_catalog(request):
    """🛍️ СОВРЕМЕННЫЙ b2b МАРКЕТПЛЕЙС — ДИНАМИЧЕСКИЙ ВЫВОД ИЗ БАЗЫ ТОВАРОВ """
    try:
        db_products = MezaninProduct.objects.all()
    except Exception:
        db_products = []

    translated_streams = []

    # Если товаров в базе пока нет, Ёжик выводит красивый базовый маркетинговый накладной набор
    if not db_products or not db_products.exists():
        default_items = [
            {"title": "Алмазные профессиональные диски Мезанина (ГОСТ)", "plat": "🇨🇳 AliExpress", "base": 187, "marg": 33, "days": 12, "icon": "💿"},
            {"title": "Латексная износостойкая краска Lakra (Фасадная)", "plat": "🇺🇸 Amazon", "base": 869, "marg": 15, "days": 18, "icon": "🪣"},
            {"title": "Высокопрочный крепёж ростверков 11-КЖ0.3 (Опт)", "plat": "🇨🇳 Alibaba", "base": 4455, "marg": 1, "days": 14, "icon": "🏗️"},
        ]
        for item in default_items:
            f_price = round(item["base"] * (1 + item["marg"] / 100.0), 2)
            translated_streams.append({
                "title": item["title"], "platform": item["plat"], "old_price": f"{item['base']:.2f} ₽",
                "final_price": f"{f_price:.2f} ₽", "margin": f"+{item['marg']}%", "days": item["days"],
                "is_local_file": False, "icon": item["icon"], "available": True
            })
    else:
        for prod in db_products:
            has_image = bool(prod.image and hasattr(prod.image, 'url'))
            try:
                url_path = prod.image.url if has_image else ""
            except Exception:
                has_image = False
                url_path = ""

            translated_streams.append({
                "title": prod.title, 
                "platform": prod.source_platform, 
                "old_price": f"{prod.base_price:.2f} ₽",
                "final_price": f"{prod.final_price:.2f} ₽", 
                "margin": f"+{prod.margin_percent}%", 
                "days": prod.delivery_days,
                "is_local_file": has_image, 
                "image_url": url_path, 
                "icon": "📦",
                "available": prod.is_available
            })

    return render(request, "storage_control/mirohube.html", {"translated_streams": translated_streams})

def upload_family_video_view(request): return redirect("/trends/")
def stroyka_platform_view(request): return HttpResponse("Matrix")
def father_panel_view(request): return HttpResponse("Father")
def custom_page_not_found_view(request, exception=None): return HttpResponse("404", status=404)
def custom_otp_admin_login_view(request): return HttpResponse("OTP")
def construction_panel_view(request): return HttpResponse("Construction")
def autonomous_guardian_status_view(request): return JsonResponse({"status": "ACTIVE"})
def dxf_blueprint_scan_view(request): return HttpResponse("DXF")
def anarchic_intelligence_view(request): return HttpResponse("Anarchic")
def capsule_panel_view(request): return HttpResponse("Capsule")
def director_dashboard_view(request): return HttpResponse("Director")
def magnat_analyzer_view(request): return JsonResponse({"status": "Operational"})
def ezhik_blogger_shop(request, username=None): return HttpResponse("SHOP")
def otez_miri_love(request): return HttpResponse("Safe locked.")
def ezhik_sympathy_notification(request): return JsonResponse({"status":"operational"})
def architect_cocktail_lounge(request): return HttpResponse("Bar.")
def export_user_records_pdf(request): return HttpResponse("PDF")
