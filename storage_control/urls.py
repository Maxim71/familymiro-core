from django.urls import path
from django.views.generic import TemplateView
from storage_control import views

urlpatterns = [
    # Выводим твой оригинальный Монолит ИТР напрямую на главную страницу, обходя сломанную функцию
    path('', TemplateView.as_view(template_name='storage_control/miro_monolith.html'), name='index_family'),
    
    # Сшиваем все твои оригинальные хай-тек HTML-страницы по их прямым адресам
    path('matrix/', TemplateView.as_view(template_name='storage_control/portal.html'), name='portal'),
    path('capsule/', TemplateView.as_view(template_name='storage_control/capsule.html'), name='capsule'),
    path('neuro-radar/', TemplateView.as_view(template_name='storage_control/neuro_radar.html'), name='neuro_radar'),
    path('voice-gateway/', TemplateView.as_view(template_name='storage_control/voice_gateway.html'), name='voice_gateway'),
    path('father-panel/', TemplateView.as_view(template_name='storage_control/father_panel.html'), name='father_panel'),
    path('blueprint/', TemplateView.as_view(template_name='storage_control/dxf_blueprint_scan.html'), name='blueprint'),
]
