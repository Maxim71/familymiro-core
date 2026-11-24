# -*- coding: utf-8 -*-
import io
from decimal import Decimal
import openpyxl
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from storage_control.models import Document, PurchaseRequest
from storage_control.services.export_customer_gpr import build_customer_gpr_excel


class Node06CustomerGprExportTest(TestCase):
    """Отмашка №6: Динамический календарный график ГПР для Заказчика по любым разделам."""

    def setUp(self):
        # Имитируем нового пользователя: загружены КЖ8, КЖ0.1 (вперемешку) и АИ (интерьеры)
        f_kj8 = SimpleUploadedFile("09-КЖ8.pdf", b"%PDF-1.4\n%%EOF", content_type="application/pdf")
        f_kj0 = SimpleUploadedFile("09-КЖ0.1.pdf", b"%PDF-1.4\n%%EOF", content_type="application/pdf")
        f_ai = SimpleUploadedFile("24.0454-Р-АИ.pdf", b"%PDF-1.4\n%%EOF", content_type="application/pdf")

        self.doc_kj8 = Document.objects.create(title="09-КЖ8.pdf", file=f_kj8)
        self.doc_kj0 = Document.objects.create(title="09-КЖ0.1.pdf", file=f_kj0)
        self.doc_ai = Document.objects.create(title="24.0454-Р-АИ.pdf", file=f_ai)

        PurchaseRequest.objects.create(
            document=self.doc_kj0, record_type="TEP", discipline="КЖ",
            material_name="Выемка грунта экскаватором", unit="м3", required_qty=Decimal("10233.00")
        )
        PurchaseRequest.objects.create(
            document=self.doc_kj8, record_type="BUY", discipline="КЖ",
            material_name="Бетон В25", unit="м3", required_qty=Decimal("700.00"), deficit_qty=Decimal("700.00")
        )
        PurchaseRequest.objects.create(
            document=self.doc_ai, record_type="BUY", discipline="АИ",
            material_name="Плиты керамогранитные", unit="м2", required_qty=Decimal("240.00"), deficit_qty=Decimal("240.00")
        )

    def test_gpr_sorts_volumes_from_zero_cycle_to_interiors(self):
        """ГПР автоматически ставит КЖ0.1 первым, затем КЖ8, затем АИ (интерьеры)."""
        xlsx_bytes = build_customer_gpr_excel()
        wb = openpyxl.load_workbook(io.BytesIO(xlsx_bytes))
        ws = wb["Календарный график (ГПР)"]

        self.assertEqual(ws.cell(row=2, column=3).value, "09-КЖ0.1.pdf")
        self.assertEqual(ws.cell(row=3, column=3).value, "09-КЖ8.pdf")
        self.assertEqual(ws.cell(row=4, column=3).value, "24.0454-Р-АИ.pdf")
        # В графике Заказчика нет внутренних колонок дефицита и цен
        headers = [ws.cell(row=1, column=c).value for c in range(1, 11)]
        self.assertNotIn("К закупке (Дефицит)", headers)

    def test_gpr_endpoint_returns_xlsx(self):
        client = Client()
        resp = client.get(reverse("storage_control:export_customer_gpr"))
        self.assertEqual(resp.status_code, 200)
        self.assertIn("spreadsheetml.sheet", resp["Content-Type"])
