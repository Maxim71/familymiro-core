# -*- coding: utf-8 -*-
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index_family, name="index_family"),
    path("trends/", views.show_products_catalog, name="show_products_catalog"),
    path("matrix/", views.stroyka_platform_view, name="stroyka_platform_view"),
    path("memory-upload/", views.upload_family_video_view, name="upload_family_video"),
]
