# -*- coding: utf-8 -*-
from django.contrib import admin
from django.urls import path
from django.contrib.sitemaps.views import sitemap
from storage_control import views
from storage_control.views import (
    index_family,
    index_construction,
    index_director,
    ezhik_partner_diplomacy_gateway,
    verify_face,
    show_products_catalog,
    father_panel_view
)

urlpatterns = [
    # 👑 Главная застава (Пользовательский интерфейс и Открытое Небо РФ)
    path('', index_family, name='index_family'),
    
    # 🌌 Главная админ-панель управления Django (Скрытый уютный шлюз)
    path('welcome-ezhik/', admin.site.urls),
    
    # 🎬 Открытые пульты управления контурами
    path('director/', index_director, name='index_director'),
    path('construction/', index_construction, name='index_construction'),
    path('products/', show_products_catalog, name='products_catalog'),
    path('father-panel/', father_panel_view, name='father_panel'),
    
    # 📄 Вековой Сейф Мирославы, Журналы и Аватар Ёжика
    path('otez-miri-love', views.otez_miri_love, name='otez_miri_love'),
    path('api/ezhik/sympathy/', views.ezhik_sympathy_notification, name='ezhik_sympathy'),
    path('api/ezhik/journal/', views.ezhik_journal_log, name='ezhik_journal'),
    
    # 🛍️ Суверенная SaaS-Платформа Магазинов Блогеров с Динамическими вилками
    path('shop/', views.ezhik_blogger_shop, name='ezhik_shop'),
    path('shop/<str:username>/', views.ezhik_blogger_shop, name='ezhik_user_shop'),
    
    # 🤝 Модерация, дипломатия и верификация биометрии
    path('api/verify-face/', verify_face, name='verify_face'),
    path('architect-lounge/', views.architect_cocktail_lounge, name='cocktail_lounge'),
    path('api/ezhik/diplomacy/', ezhik_partner_diplomacy_gateway, name='ezhik_diplomacy'),
]
