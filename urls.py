# -*- coding: utf-8 -*-
from django.urls import path
from .views import index_family, index_construction, index_director, project_manager_analytics, constructor_matrix, send_invite_sms

urlpatterns = [
    path('', index_family, name='index_family'),
    path('construction/', index_construction, name='index_construction'),
    path('director/', index_director, name='index_director'),
    # Новые аналитические B2B-контуры снабжения Mezzanine
    path('construction/analytics/', project_manager_analytics, name='pm_analytics'),
    path('construction/matrix/', constructor_matrix, name='constructor_matrix'),
    path('api/sms/invite/', send_invite_sms, name='send_invite_sms'),
]
