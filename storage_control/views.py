# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import JsonResponse
from storage_control.logic_core import EzhikIntentClassifier, PtoDrawingBlueprintParser, PriceBlenderExcelExporter, GeneralConstructionLogManager, WarehouseFourInOneAnalyzer

def index_vancouver(request):
    return render(request, "miro_monolith.html")

def classify_intent_endpoint(request):
    user_text = request.GET.get("text", "Проект Ванкувер АР спецификация бетона остатки")
    classifier = EzhikIntentClassifier()
    ai_report = classifier.classify(user_text)
    
    pto_parser = PtoDrawingBlueprintParser()
    stamp_report = pto_parser.parse_blueprint_stamp(pdf_path="/app/storage/drawing_list_5.pdf", section_type="АР")
    
    analyzer_4in1 = WarehouseFourInOneAnalyzer()
    warehouse_report = analyzer_4in1.analyze_remaining_balance(
        material_name=stamp_report.get("extracted_material_node"),
        project_volume=stamp_report.get("extracted_volume_node")
    )
    
    blender = PriceBlenderExcelExporter()
    excel_report = blender.export_blender_to_excel(data_dict=stamp_report)
    
    log_manager = GeneralConstructionLogManager()
    ojr_report = log_manager.auto_fill_ojr_record(stamp_data=stamp_report)
    
    return JsonResponse({
        "status": "CLASSIFY_SUCCESS",
        "input_text": user_text,
        "bronepoezd_short_code": ai_report.get("short_code"),
        "ai_vector_analysis": ai_report,
        "pto_blueprint_stamp_ocr_eye": stamp_report,
        "warehouse_4_in_1_remaining_analysis": warehouse_report,
        "price_blender_pandas_excel": excel_report,
        "ojr_ks6a_auto_filled_log": ojr_report,
        "marker": "(0.0.0.23)"
    })
