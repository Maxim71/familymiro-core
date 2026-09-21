from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_vancouver, name='index_vancouver'),
    path('pto/<int:act_id>/', views.pto_cabinet, name='pto_cabinet'),
    path('pto/<int:act_id>/exit/', views.pto_cabinet, name='pto_cabinet_exit'),
    path('radar/', views.neuro_radar_dashboard, name='neuro_radar_dashboard'),
    path('api/send-stream/', views.send_to_stream_api, name='send_to_stream_api'),
    path('api/live-stream-data/', views.live_stream_dashboard_api, name='live_stream_dashboard_api'),
    path('api/import-excel-pto/', views.import_excel_pto_api, name='import_excel_pto_api'),
    path('api/ezhik-voice-notepad/', views.ezhik_voice_notepad_api, name='ezhik_voice_notepad_api'),
    path('api/neuro-radar-voice/', views.neuro_radar_voice_api, name='neuro_radar_voice_api'),
    path('api/computer-vision-m19/', views.computer_vision_m19_api, name='computer_vision_m19_api'),
    path('api/checkout-sbp-payment/', views.checkout_sbp_payment_api, name='checkout_sbp_payment_api'),
    path('api/trigger-bi-tabel-analysis/', views.trigger_bi_tabel_analysis_api, name='trigger_bi_tabel_analysis_api'),
    path('api/erp-calculate-subcontractor/', views.erp_calculate_subcontractor_api, name='erp_calculate_subcontractor_api'),
    path('api/erp-add-brigade-task/', views.erp_add_brigade_task_api, name='erp_add_brigade_task_api'),
    path('api/tender-exchange-dashboard/', views.tender_exchange_dashboard_api, name='tender_exchange_dashboard_api'),
    path('api/bot-api-master-diagnostic/', views.bot_api_master_diagnostic_action_api, name='bot_api_master_diagnostic_action_api'),
]
