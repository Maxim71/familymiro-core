from django.contrib import admin
from django.urls import path
from storage_control import views

urlpatterns = [
    path('api/upload-video/', views.upload_video_to_vault_api, name='upload_video'),
    path('admin/', admin.site.urls),
    path('', views.index_vancouver, name='index_vancouver'),
    path('pto/<int:act_id>/', views.pto_cabinet, name='pto_cabinet'),
    path('api/save-vhd/', views.save_vhd_journal_record, name='save_vhd'),
    path('api/get-stream/', views.live_stream_dashboard_api, name='get_stream'),
    path('api/send-stream/', views.send_to_stream_api, name='send_stream'),
    path('api/add-to-cart/<int:product_id>/', views.add_to_cart_api, name='add_to_cart'),
    path('api/shop-checkout/', views.checkout_sbp_payment_api, name='shop_checkout'),
    path('neuro-radar/', views.neuro_radar_dashboard, name='neuro_radar'),
    path('capsule/', views.capsule_time_vault, name='capsule'),
]
