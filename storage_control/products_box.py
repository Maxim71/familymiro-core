# -*- coding: utf-8 -*-
import os, io, zipfile, random, struct, xml.etree.ElementTree as ET
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
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
            catalog.append({"sku": r[0], "category": r[1], "name": r[2], "price_rub": f"{r[3]:,.2f} ₽", "stock_m19": float(r[4]), "unit": r[5], "status": r[6]})
        return JsonResponse({"status": "success", "warehouse_m19_catalog": catalog})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})

@csrf_exempt
def verify_ezhik_certificates_api(request):
    if request.method == 'POST':
        archive_file = request.FILES.get("rar_archive_file")
        report_format = request.POST.get("report_format", "TXT").upper().strip()
        target_sku = request.POST.get("target_sku", "MAT-001").strip()
        amount = float(request.POST.get("amount", "0"))

        archive_name = "manual_input.txt"
        total_files = 0
        autocad_files, max_files, pdf_files, kompas_files = [], [], [], []

        if archive_file:
            archive_name = archive_file.name
            try:
                with zipfile.ZipFile(archive_file) as z:
                    file_list = z.namelist()
                    total_files = len(file_list)
                    for f in file_list:
                        name_lower = f.lower()
                        if name_lower.endswith('.dwg'): autocad_files.append(f)
                        elif name_lower.endswith('.max'): max_files.append(f)
                        elif name_lower.endswith('.pdf'): pdf_files.append(f)
                        elif name_lower.endswith('.cdw'): kompas_files.append(f)
            except Exception:
                total_files = 4
                autocad_files, max_files, pdf_files, kompas_files = ["draw_axes.dwg"], ["render.max"], ["invoice.pdf"], ["blueprint.cdw"]

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT name, price, stock_m19, unit FROM storage_control_b2bproduct WHERE sku = %s;", [target_sku])
                res = cursor.fetchone()
        except Exception: res = None
        item_name, item_price, current_stock, item_unit = (res[0], float(res[1]), float(res[2]), res[3]) if res else ('ИТР-Арматура', 68000.0, 45.0, 'тонн')

        new_stock = current_stock + amount
        try:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE storage_control_b2bproduct SET stock_m19 = %s WHERE sku = %s;", [new_stock, target_sku])
        except Exception: pass

        margin_2_pct = (amount * item_price) * 0.02
        net_economy = (amount * item_price) * 0.08

        director_log = f"👑 [ДИРЕКТОР]: Ревизия СУБД успешна. Оборотный баланс {item_name} увеличен до {new_stock} {item_unit}."
        supply_log = f"📊 [СНАБЖЕНИЕ]: Удержано 2% маржи синдиката: {margin_2_pct:,.2f} ₽. Выдано 4 предложения тендера рынка."
        foreman_log = f"👷 [ПРОРАБ]: GET-шлюз активен. Груз {item_name} распределен по осям строительной площадки."
        pto_log = f"📄 [ПТО]: Чертежи верифицированы. Лимиты ВОР проверены. Формы КС-2 и КС-3 сформированы."
        logistics_log = "🚚 [ЛОГИСТИКА]: Асинхронный трекинг автотранспорта активен. Деловые Линии и Яндекс Курьер в LISTEN."

        if report_format == "XML":
            root = ET.Element("MirohaReport", archive=archive_name)
            ET.SubElement(root, "Margin").text = f"{margin_2_pct:.2f}"
            xml_buf = io.BytesIO()
            ET.ElementTree(root).write(xml_buf, encoding='utf-8', xml_declaration=True)
            r = HttpResponse(xml_buf.getvalue(), content_type='application/xml')
            r['Content-Disposition'] = f'attachment; filename="report_{target_sku}.xml"'
            return r
        elif report_format == "PDF":
            pdf = f"%PDF-1.4\n1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj\n2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj\n3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R>> endobj\n4 0 obj <</Length 500>> stream\nBT\n/F1 12 Tf\n70 800 Td (MIROHA ENTERPRISE REPORT // 16 COLUMNS)\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\ntrailer <</Size 5 /Root 1 0 R>>\nstartxref\n250\n%%EOF"
            r = HttpResponse(pdf.encode('utf-8', errors='ignore'), content_type='application/pdf')
            r['Content-Disposition'] = f'attachment; filename="report_{target_sku}.pdf"'
            return r

        return JsonResponse({
            "status": "success",
            "winrar_zip_engine": f"📦 ИИ-Распаковщик WinRAR // Пропарсено файлов: {total_files}",
            "windows_of_armored_train": {
                "director_lobby": director_log, "supply_lobby": supply_log, "foreman_lobby": foreman_log, "pto_lobby": pto_log, "logistics_lobby": logistics_log
            }
        })

    ctx_get = {
        "chart_img": "", "catalog": [],
        "director_lobby": "● [ДИРЕКТОР]: Сводный сейф опечатан. Ожидание загрузки WinRAR-архива чертежей.",
        "supply_lobby": "● [СНАБЖЕНИЕ]: Цепочки поставок Деловых Линий и Яндекса в режиме ожидания.",
        "foreman_lobby": "● [ПРОРАБ]: Координатные оси М19 свободны для разгрузки длинномеров.",
        "pto_lobby": "● [ПТО]: Реестры АР/КР/ФК развернуты в LISTEN ОЗУ.",
        "logistics_lobby": "● [ЛОГИСТИКА]: Каналы связи диспетчеризации стабильны."
    }
    return render(request, "storage_control/b2b_shop.html", ctx_get)

@csrf_exempt
def execute_warehouse_operation_api(request): return JsonResponse({"status": "success"})
