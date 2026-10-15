# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import JsonResponse
from storage_control.logic_core import EzhikIntentClassifier, Universal1CHub

def index_vancouver(request):
    return render(request, "miro_monolith.html")

def classify_intent_endpoint(request):
    user_text = request.GET.get("text", "")
    api_input = request.GET.get("api_url", "")
    token_input = request.GET.get("token", "")
    
    # 1. Радар Яндекса
    classifier = EzhikIntentClassifier()
    ai_report = classifier.classify(user_text)
    
    # 2. Инициализация универсального ИИ-хаба 1С
    hub_1c = Universal1CHub()
    
    # Отрабатываем все 3 каскадных способа в ОЗУ без повторений
    api_status = hub_1c.execute_api_reset(api_input, token_input)
    manual_status = hub_1c.ingest_manual_catalog(subject_id="Partner_Sub_82", file_name="ostatki_skлада.xlsx")
    db_status = hub_1c.bypass_db_blockers()
    
    return JsonResponse({
        "status": "CLASSIFY_SUCCESS",
        "input_text": user_text,
        "marker": "(0.0.0.23)",
        "ai_analysis": ai_report,
        "1c_integration_matrix": {
            "способ_1_rest_api": api_status,
            "способ_2_ручной_каталог": manual_status,
            "способ_3_обход_блокировок": db_status
        }
    })
