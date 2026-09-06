# -*- coding: utf-8 -*-
from django.contrib import admin
from django.urls import path
from storage_control import views

urlpatterns = [
    path('', views.index_family, name='index_family'),
    path('welcome-ezhik/', admin.site.urls),
    
    # Твоя лазерная b2b-карта путей холдинга FAMILYMIRO 1.6
    path('oto/', views.father_panel_view, name='father_panel'),
    path('ii/', views.anarchic_intelligence_view, name='anarchic_intelligence'),
    path('foto-othet/', views.construction_panel_view, name='construction_panel'),
    path('blog-loveii/', views.show_products_catalog, name='products_catalog'),
    path('vitachit/', views.capsule_panel_view, name='capsule_panel'),
    
    # 📑 СЛУЖБА ЭКСПОРТА ДОКУМЕНТОВ ЁЖИКА (СБОРКА В PDF НА ЛЕТУ)
    path('export-pdf/', views.export_user_records_pdf, name='export_pdf'),

    path('magnat-audit/', views.magnat_analyzer_view, name='magnat_audit'),
    path('shop/', views.ezhik_blogger_shop, name='ezhik_shop'),
    path('shop/<str:username>/', views.ezhik_blogger_shop, name='ezhik_user_shop'),
    path('architect-lounge/', views.architect_cocktail_lounge, name='cocktail_lounge'),
]
