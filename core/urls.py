# -*- coding: utf-8 -*-
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from storage_control import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index_family, name="index_family"),
    path("trends/", views.show_products_catalog, name="show_products_catalog"),
    path("matrix/", views.stroyka_platform_view, name="stroyka_platform_view"),
    path("memory-upload/", views.upload_family_video_view, name="upload_family_video"),
]

if settings.DEBUG or True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
