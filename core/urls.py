from django.contrib import admin
from django.urls import path
from storage_control import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('get-free-2fa-qr/', views.generate_free_google_qr_view, name='free_qr'),
    path('', views.index_vancouver, name='index_vancouver'),
    path('user/<str:client_id>/', views.user_isolated_cabinet, name='user_cabinet'),
    path('api/ezhik-auth/', views.execute_ezhik_auth_api, name='ezhik_auth'),
    path('api/v5/openpyxl-parser/', views.openpyxl_vor_parser_api, name='openpyxl_parser'),
    path('api/users-groups/', views.users_groups_matrix, name='users_groups'),
    path('api/trigger-mesh/', views.trigger_cyber_mesh_probe_api, name='cyber_mesh'),
    path('api/propropab-notify/', views.smtp_propropab_notifier_api, name='smtp_notify'),
]
