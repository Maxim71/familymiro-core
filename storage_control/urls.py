from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_vancouver, name='index_vancouver'),
    path('pto/<int:act_id>/', views.pto_cabinet, name='pto_cabinet'),
    path('radar/', views.neuro_radar_dashboard, name='neuro_radar_dashboard'),
    path('api/metabase-xray-heatmap/', views.metabase_xray_heatmap_api, name='metabase_xray_heatmap_api'),
    path('ipropab/<str:company>/<str:name>/<str:task_id>/status/', views.ipropab_agent_cabinet, name='ipropab_agent_cabinet'),
    path('ipropab/<str:company>/<str:name>/<str:task_id>/status/submit/', views.ipropab_submit_photo_api, name='ipropab_submit_photo_api'),
]
