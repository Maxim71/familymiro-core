# -*- coding: utf-8 -*-
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index_family, name="index_family"),
    path("trends/", views.show_products_catalog, name="products_catalog"),
    
    # НОВЫЙ СОЧНЫЙ И МЕЖДУНАРОДНЫЙ b2b-МАРШРУТ СТРОИТЕЛЬНОЙ МАТРИЦЫ
    path("matrix/", views.stroyka_platform_view, name="stroyka_platform"),
    
    path("welcome-ezhik/", views.custom_otp_admin_login_view, name="otp_admin_login"),
    path("oto/", views.father_panel_view, name="father_panel"),
    path("ii/", views.anarchic_intelligence_view, name="anarchic_intelligence"),
    path("dxf-scan/", views.dxf_blueprint_scan_view, name="dxf_blueprint_scan"),
]
