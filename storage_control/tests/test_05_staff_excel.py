# -*- coding: utf-8 -*-
import io
from decimal import Decimal
import openpyxl
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from storage_control.models import Document, PurchaseRequest
from storage_control.services.export_staff_excel import build_staff_excel_bytes


class Node05StaffExcelExportTest(TestCase):
    """Отмашка №5: Проверка генерации 3-листового штабного Excel (.xlsx)."""
    def setUp(self):
        dummy_pdf = SimpleUploadedFile("24.0454-P-SKS.pdf", b"%PDF-1.4\n%%EOF", content_type="application/pdf")
        self.doc = Document.objects.create(title="24.0454-P-SKS.pdf", file=dummy_pdf)

        PurchaseRequest.objects.create(
            document=self.doc,
            record_type="BUY",
            discipline="СКС",
            room_info="Серверная (пом. 115)",
            node_cabinet="Шкаф ТШ СС 1.0",
            material_name="Коммутатор PoE СКС",
            unit="шт.",
            required_qty=Decimal("4.00"),
            deficit_qty=Decimal("4.00"),
            responsible_itr="Максим Косарев [ITR-MAX-77]",
        )
        PurchaseRequest.objects.create(
            document=self.doc,
            record_type="TEP",
            discipline="АР",
            material_name="Строительный объем подземный",
            unit="м3",
            required_qty=Decimal("4716.30"),
        )
        PurchaseRequest.objects.create(
            document=self.doc,
            record_type="LIMIT",
            discipline="АР",
            material_name="Допустимая нагрузка на панель",
            unit="кг",
            required_qty=Decimal("350.00"),
        )

    def test_excel_has_three_sheets_with_links_and_logistics(self):
        """Файл Excel содержит 3 листа, очищенную номенклатуру, строку ИТОГО и расчёт логистики."""
        xlsx_bytes = build_staff_excel_bytes(doc=self.doc)
        wb = openpyxl.load_workbook(io.BytesIO(xlsx_bytes))

        self.assertEqual(wb.sheetnames, ["1. Снабжение (Закупки)", "2. ПТО и BIM-сверка", "3. Логистика и ГПР"])

        ws_buy = wb["1. Снабжение (Закупки)"]
        self.assertEqual(ws_buy.cell(row=2, column=4).value, "Коммутатор PoE СКС")
        self.assertEqual(ws_buy.cell(row=3, column=3).value, "ИТОГО ПО ВЕДОМОСТИ:")

        ws_log = wb["3. Логистика и ГПР"]
        self.assertIn("ТК Деловые Линии", ws_log.cell(row=2, column=5).value)

    def test_excel_download_endpoint_returns_xlsx(self):
        """HTTP-маршрут выгрузки возвращает корректный файл .xlsx."""
        client = Client()
        url = f"{reverse('storage_control:export_staff_excel')}?doc_id={self.doc.id}"
        resp = client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("spreadsheetml.sheet", resp["Content-Type"])
