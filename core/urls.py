from django.contrib import admin
from django.urls import path
from storage_control import views

urlpatterns = [
    # 📡 БАЗОВЫЕ ИТР-МАРШРУТЫ И ШЛЮЗЫ АИС
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

    # 📦 ТВОИ ТРЕБУЕМЫЕ ПОРТАЛЫ, ЛИМИТЫ, ДЕШБОРДЫ, СКЛАДЫ И ГРУППЫ УЧЕТА
    path('api/supply-limits/', views.supply_limits_portal, name='supply_limits'),
    path('api/warehouse-m19/', views.warehouse_m19_stock, name='warehouse_m19'),
    path('api/users-groups/', views.users_groups_matrix, name='users_groups'),
    path('api/itr-control/', views.itr_control_panel, name='itr_control'),
    path('api/admin-vault/', views.admin_control_vault, name='admin_vault'),

    # ➕ 10 СТРАТЕГИЧЕСКИХ ENTERPRISE-РАСШИРЕНИЙ ДЛЯ МИРОВЫХ ПЛОЩАДОК
    path('api/v5/alfa-sbp-qr/', views.alfa_sbp_generate_qr_api, name='alfa_sbp_qr'),
    path('api/v5/openpyxl-parser/', views.openpyxl_vor_parser_api, name='openpyxl_parser'),
    path('api/v5/kafka-logger/', views.kafka_stream_logger_api, name='kafka_logger'),
    path('api/v5/ezdxf-cad-mesh/', views.ezdxf_cad_blueprint_api, name='ezdxf_cad_mesh'),
    path('api/v5/yolo-vision/', views.yolo_neural_grid_api, name='yolo_vision'),
    path('api/v5/reportlab-pdf/', views.reportlab_ks2_generator_api, name='reportlab_pdf'),
    path('api/v5/1c-sync-bridge/', views.one_c_sync_bridge_api, name='one_c_sync'),
    path('api/v5/cac-calculator/', views.cac_metric_numpy_api, name='cac_calculator'),
    path('api/v5/sitemap-generator/', views.seo_sitemap_xml_api, name='sitemap_gen'),
    path('api/v5/smtp-alert-rel/', views.smtp_propropab_notifier_api, name='smtp_alert'),
]
