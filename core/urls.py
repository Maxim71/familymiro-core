# -*- coding: utf-8 -*-
from django.contrib import admin
from django.urls import path
from storage_control import views
from storage_control import products_box
from storage_control import blogger_box

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index_vancouver, name='index_vancouver'),
    path('get-free-2fa-qr/', views.generate_free_google_qr_view, name='free_qr'),
    path('user/<str:client_id>/', views.user_isolated_cabinet, name='user_cabinet'),
    path('api/ezhik-auth/', views.execute_ezhik_auth_api, name='ezhik_auth'),
    path('api/v5/openpyxl-parser/', products_box.verify_ezhik_certificates_api, name='openpyxl_parser'),
    path('api/v5/products/catalog/', products_box.get_syndicate_catalog_api),
    path('api/v5/products/warehouse/', products_box.execute_warehouse_operation_api),
    path('api/v5/blogger/<str:blogger_id>/', blogger_box.get_blogger_panel_api),
    path('api/users-groups/', views.users_groups_matrix, name='users_groups'),
    path('api/trigger-mesh/', views.trigger_cyber_mesh_probe_api, name='cyber_mesh'),
    path('api/propropab-notify/', views.smtp_propropab_notifier_api, name='smtp_notify'),
]
