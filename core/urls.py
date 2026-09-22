from django.contrib import admin
from django.urls import path
from storage_control import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index_vancouver, name='index_vancouver'),
    path('cabinet/<str:client_id>/', views.user_isolated_cabinet, name='user_cabinet'),
    path('api/ezhik-auth/', views.execute_ezhik_auth_api, name='ezhik_auth'),
    path('neuro-radar/', views.neuro_radar_dashboard, name='neuro_radar'),
    
    # 📸 НАШ НОВЫЙ СКВОЗНОЙ ПУТЬ СКАНИРОВАНИЯ QR-КОДА ДЛЯ GOOGLE AUTHENTICATOR
    path('get-free-2fa-qr/', views.generate_free_google_qr_view, name='get_2fa_qr'),

    # API Сокеты
    path('api/upload-video/', views.upload_video_to_vault_api, name='upload_video'),
    path('api/save-vhd/', views.save_vhd_journal_record, name='save_vhd'),
    path('api/get-stream/', views.live_stream_dashboard_api, name='get_stream'),
    path('api/send-stream/', views.send_to_stream_api, name='send_stream'),
    path('api/add-to-cart/<int:product_id>/', views.add_to_cart_api, name='add_to_cart'),
    path('api/shop-checkout/', views.checkout_sbp_payment_api, name='shop_checkout'),
    path('api/supply-limits/', views.supply_limits_portal, name='supply_limits'),
    path('api/warehouse-m19/', views.warehouse_m19_stock, name='warehouse_m19'),
    path('api/users-groups/', views.users_groups_matrix, name='users_groups'),
    path('api/itr-control/', views.itr_control_panel, name='itr_control'),
    path('api/admin-vault/', views.admin_control_vault, name='admin_vault'),
    path('api/v5/openpyxl-parser/', views.openpyxl_vor_parser_api, name='openpyxl_parser'),
]
