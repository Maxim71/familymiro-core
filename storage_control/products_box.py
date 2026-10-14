# -*- coding: utf-8 -*-
import os, io, json, random
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db import connection

@csrf_exempt
def get_syndicate_catalog_api(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT sku, category, name, price, stock_m19, unit, status FROM storage_control_b2bproduct;")
            rows = cursor.fetchall()
        catalog = []
        for r in rows:
            catalog.append({"sku": r[0], "category": r[1], "name": r[2], "price_rub": f"{r[3]:,.2f} RUB", "stock_m19": float(r[4]), "unit": r[5], "status": r[6]})
        return JsonResponse({"status": "success", "warehouse_m19_catalog": catalog})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})

@csrf_exempt
def verify_ezhik_certificates_api(request):
    return render(request, "storage_control/b2b_shop.html", {"catalog": []})

@csrf_exempt
def execute_warehouse_operation_api(request):
    return JsonResponse({"status": "success"})
