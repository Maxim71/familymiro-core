from django.contrib import admin
from django.urls import path
from storage_control import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index_vancouver, name="index"),
    path("classify-intent/", views.classify_intent_endpoint, name="classify_intent"),
]
