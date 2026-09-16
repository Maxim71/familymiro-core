from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_vancouver, name='index_vancouver'),
    path('pto/<int:act_id>/', views.pto_cabinet, name='pto_cabinet'),
    path('pto/<int:act_id>/exit/', views.pto_cabinet, name='pto_cabinet_exit'),
    path('capsule/', views.capsule_time_vault, name='capsule_time_vault'),
    path('radar/', views.neuro_radar_dashboard, name='neuro_radar_dashboard'),
    path('api/send-stream/', views.send_to_stream_api, name='send_to_stream_api'),
    path('api/live-stream-data/', views.live_stream_dashboard_api, name='live_stream_dashboard_api'),
    path('api/import-excel-pto/', views.import_excel_pto_api, name='import_excel_pto_api'),
    path('api/ezhik-voice-notepad/', views.ezhik_voice_notepad_api, name='ezhik_voice_notepad_api'),
    path('api/neuro-radar-voice/', views.neuro_radar_voice_api, name='neuro_radar_voice_api'),
    path('api/computer-vision-m19/', views.computer_vision_m19_api, name='computer_vision_m19_api'),
]
