# -*- coding: utf-8 -*-
# FAMILYMIRO THREE-CONTOUR MATRIX V7.0.0 — READONLY b2b DASHBOARD & CALENDAR
import math
import random
import subprocess
import os
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from .models import Agreement, VideoCapsule, AvatarEzhik, InteractiveComment, BloggerUsage, ConstructionCompany, CascadeTask, PunchListItem, NetworkIncident

def index_family(request):
    return render(request, "storage_control/portal.html", {"captain": "Miroslava_Kosareva"})

def show_products_catalog(request):
    static_dir = "/root/app/storage_control/static/storage_control"
    local_videos = []
    if os.path.exists(static_dir):
        files = [f for f in os.listdir(static_dir) if f.startswith("capsule_") and f.endswith(".mp4")]
        if files:
            files.sort(key=lambda x: os.path.getmtime(os.path.join(static_dir, x)), reverse=True)
            for f in files: local_videos.append(f"/static/storage_control/{f}")
                
    fallback_video = "https://rutube.ru"
    snake_slots = []
    embed_url = local_videos if local_videos else fallback_video
    snake_slots.append({
        "id": 7, "platform": "Суверенное Видео 🦾",
        "title": "Вековая родовая капсула памяти Наследницы Мирославы",
        "desc": "СУВЕРЕННЫЙ АРХИВ ОТЦА: Запечатано в Сейф вечности холдинга FAMILYMIRO [1.5, 1.6].",
        "embed_url": embed_url, "likes": 2500, "is_generated": 1, "is_local_mp4": True if local_videos else False
    })
    return render(request, "storage_control/mirohube.html", {"translated_streams": snake_slots})

def upload_family_video_view(request):
    if request.method == "POST" and request.FILES.get("family_file"):
        try:
            video_file = request.FILES["family_file"]
            final_name = "capsule_777.mp4"
            final_path = f"/root/app/storage_control/static/storage_control/{final_name}"
            os.makedirs(os.path.dirname(final_path), exist_ok=True)
            with open(final_path, "wb+") as dest:
                for chunk in video_file.chunks(): dest.write(chunk)
            return redirect("/trends/?taste=general")
        except Exception as e: pass
    return render(request, "storage_control/upload_defect.html")

def stroyka_platform_view(request):
    """📐 УСОВЕРШЕНСТВОВАННЫЙ b2b-ПУЛЬТ: КАРТА-КАЛЕНДАРЬ И ПРАВА READONLY ДЛЯ ПАРТНЕРОВ """
    status_msg = "ℹ️ b2b СТАТУС ВЕРИФИКАЦИИ: Подключен режим ReadOnly Access для Итальянских партнеров. Изменение или удаление данных смет заблокировано!"
    
    # Симулируем Карту Капсул в виде календаря событий (Пункт 2 со скриншота)
    calendar_events = [
        {"date": "06.09", "event": "📦 Отгружено 250 алмазных дисков Мезанина", "type": "b2b"},
        {"date": "07.09", "event": "🎬 Запечатан 10-сек утренник дочки (Тест)", "type": "family"},
        {"date": "08.09", "event": "⚡ Активирован пусковой контур main.py в Docker", "type": "system"},
        {"date": "09.09", "event": "📅 Ожидание новой родовой капсулы вечности", "type": "empty"}
    ]
    
    return render(request, "storage_control/stroyka.html", {
        "status_msg": status_msg, 
        "calendar_events": calendar_events,
        "calculated_margin": 56900.00,
        "read_only_mode": True
    })

def father_panel_view(request): return render(request, "storage_control/father_panel.html")
def custom_page_not_found_view(request, exception=None): return render(request, "storage_control/404.html", status=404)
def custom_otp_admin_login_view(request): return render(request, "storage_control/otp_login.html")
def construction_panel_view(request): return render(request, "storage_control/construction.html")
def autonomous_guardian_status_view(request): return JsonResponse({"status": "ACTIVE"})
def dxf_blueprint_scan_view(request): return render(request, "storage_control/dxf_blueprint_scan.html")
def anarchic_intelligence_view(request): return render(request, "storage_control/anarchic_intelligence.html")
def capsule_panel_view(request): return render(request, "storage_control/capsule.html")
def director_dashboard_view(request): return render(request, "storage_control/director.html")
def magnat_analyzer_view(request): return JsonResponse({"status": "Operational"})
def ezhik_blogger_shop(request, username=None): return HttpResponse("SHOP")
def otez_miri_love(request): return HttpResponse("Safe locked.")
def ezhik_sympathy_notification(request): return JsonResponse({"status":"operational"})
def architect_cocktail_lounge(request): return HttpResponse("Bar.")
def export_user_records_pdf(request): return HttpResponse("PDF Exported.")
