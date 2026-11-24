# -*- coding: utf-8 -*-
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Главный пульт админки и ИИ-обучения Нежика
    path('admin/', admin.site.urls),
    
    # 🚀 ПОЛНАЯ СЦЕПКА: Подключаем все 23 интерфейса Бронепоезда на корень сайта!
    path('', include('storage_control.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
