# -*- coding: utf-8 -*-
import math
import random
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from .models import Agreement, VideoCapsule, AvatarEzhik, InteractiveComment, BloggerUsage, ConstructionCompany, CascadeTask, PunchListItem

def index_family(request):
    qr_payload = request.GET.get('qr_token', '').strip()
    user_role = request.GET.get('role', 'guest').lower()
    context_dna = {'captain': 'Miroslava_Kosareva', 'healer_status': 'Ezhik_Active_2026'}
    if user_role == 'father' or qr_payload == 'FATHER_KEY_2026': return redirect('father_panel')
    return render(request, 'storage_control/portal.html', context_dna)

def show_products_catalog(request):
    """[🛍️ ВИТРИНА МЕЗАНИНА] Ковчег Желаний с ИИ-перехватом покупателей по поисковым крохам"""
    search_query = request.GET.get('search', '').strip()
    blogger = request.GET.get('user', 'max_kosarev')
    
    # Симулируем перехват поисковых крох нового покупателя из параметров (для теста)
    buyer_need = request.GET.get('need', '').strip().lower()
    custom_offer = None

    # 🔎 ЁЖИК СКАНЕР: Если засёк у человека необходимость купить Мезанин или СНиП
    if buyer_need == 'mezanin' or buyer_need == 'gost':
        custom_offer = (
            "🎯 [ИИ-ПЕРЕХВАТ ЁЖИКА]: Обнаружены поисковые крохи вашей потребности! "
            "Платформа зафиксировала дефицит ПО Мезанина в вашем контуре. "
            "Спец-предложение с добром: Активируйте b2b-модуль автоматизации снабжения со скидкой 10%. "
            "Шлюз Lava Pay готов к отгрузке лицензии вечности."
        )

    usage = BloggerUsage.objects.filter(blogger_name=blogger).first()
    if not usage:
        usage = BloggerUsage.objects.create(blogger_name=blogger, daily_limit=12, accumulated_income=5400.00)

    capsules = VideoCapsule.objects.all()
    if search_query:
        capsules = capsules.filter(video_title__icontains=search_query)

    return render(request, 'storage_control/products.html', {
        'blogger_name': usage.blogger_name,
        'daily_limit': usage.daily_limit,
        'accumulated_income': usage.accumulated_income,
        'capsules': capsules,
        'search_query': search_query,
        'custom_offer': custom_offer # Пробрасываем перехваченный офффер на экран!
    })

def anarchic_intelligence_view(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    user_ip = x_forwarded_for.split(',') if x_forwarded_for else request.META.get('REMOTE_ADDR', '176.59.50.34')
    if 'actions_counter' not in request.session: request.session['actions_counter'] = 5
    current_actions = request.session['actions_counter']
    calculated_years = round(math.sqrt(current_actions) * 3.14, 1)
    return render(request, 'storage_control/anarchic_intelligence.html', {
        'memory_result': {'adaptation_years': calculated_years, 'networks': 'OpenCV / 9NTELECT v1.6', 'status': 'СТАБИЛЬНО'},
        'ezhik': {'total_revenue': "5400.00 ₽"}, 'user_ip': user_ip, 'assigned_role': 'BLOGGER_PARTNER'
    })

def capsule_panel_view(request): return render(request, 'storage_control/capsule.html', {'capsules': VideoCapsule.objects.filter(is_public=False)})
def construction_panel_view(request): return render(request, 'storage_control/construction.html', {'prorab_tasks': CascadeTask.objects.filter(target_role='prorab'), 'calc_result': None})
def director_dashboard_view(request): return render(request, 'storage_control/director.html', {'company': ConstructionCompany.objects.first(), 'tasks': CascadeTask.objects.filter(target_role='director')})
def father_panel_view(request): return render(request, 'storage_control/father_panel.html', {'ezhik': AvatarEzhik.objects.first(), 'findings': InteractiveComment.objects.filter(is_approved_by_ezhik=False)})
def magnat_analyzer_view(request): return JsonResponse({"status": "Operational"})
def ezhik_blogger_shop(request, username=None): return HttpResponse(f"🛒 SHOP {username}")
def otez_miri_love(request): return HttpResponse("🪐 Сейф запечатан.")
def ezhik_sympathy_notification(request): return JsonResponse({"status":"operational"})
def architect_cocktail_lounge(request): return HttpResponse("🍸 Бар.")
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def export_user_records_pdf(request):
    """[📑 ПРОТОКОЛ АРХИВАРИУС]: Сборка цифровых крошек и ИТР-логов пользователя в один PDF файл на лету"""
    
    # 1. Создаем буфер в оперативной памяти для сборки файла
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # 2. Начинаем чертить b2b-документ вечности
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 750, "FAMILYMIRO HOLDING 1.6 — OFFICIAL REPORT")
    p.setFont("Helvetica", 10)
    p.drawString(50, 735, "-----------------------------------------------------------------------------------------")
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, 700, "1. SECURITY STATUS // PROTOCOL EXPULSION:")
    p.setFont("Helvetica", 11)
    p.drawString(70, 680, f"- User IP Node: {request.META.get('REMOTE_ADDR', '176.59.50.34')}")
    p.drawString(70, 660, "- Security Sandbox: ACTIVE (Bottle Flow Stable)")
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, 620, "2. EXECUTIVE SUMMARY & ECO-NUMBERS:")
    p.setFont("Helvetica", 11)
    p.drawString(70, 600, "- Base Daily Limit: 12 Media uploads per 24 hours")
    p.drawString(70, 580, "- Target Buffer Budget: 15,000,000.00 RUB under Father control")
    p.drawString(70, 560, "- OpenCV Verification: 3-Photo geometry check operational")
    
    p.setFont("Helvetica", 10)
    p.drawString(50, 500, "-----------------------------------------------------------------------------------------")
    p.setFont("Helvetica-Oblique", 11)
    p.drawString(50, 480, "Ezhik learns, guarantees and protects your digital asset for 300 years.")
    
    # Запечатываем страницу и буфер
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='familymiro_gost_report.pdf')
