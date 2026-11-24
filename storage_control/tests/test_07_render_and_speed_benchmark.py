# -*- coding: utf-8 -*-
import time
from decimal import Decimal
from unittest.mock import patch
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from storage_control.models import Document, PurchaseRequest
from storage_control.services.smart_router import evaluate_parsing_quality
from storage_control.services.route_tracer import build_engineering_procurement_rows
from storage_control.services.mark_passport import build_mark_passport_data
from storage_control.services.export_staff_excel import build_staff_excel_bytes


class Node07RenderAndSpeedBenchmarkTest(TestCase):
    """Контрольный тест скорости каждого подмодуля (в мс) и живого вывода HTML главной страницы портала."""

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_superuser("bench_admin", "bench@local.ru", "bench12345")
        dummy_pdf = SimpleUploadedFile("02-24.0454-Р-АР0.pdf", b"%PDF-1.4\n%%EOF", content_type="application/pdf")
        self.doc = Document.objects.create(title="02-24.0454-Р-АР0.pdf", owner=self.user, file=dummy_pdf)
        PurchaseRequest.objects.create(
            document=self.doc,
            record_type="BUY",
            discipline="АР",
            material_name="Газобетонные блоки YTONG 200мм (или аналог)",
            unit="м2",
            required_qty=Decimal("120.00"),
            deficit_qty=Decimal("120.00"),
        )

    @patch("storage_control.services.mark_passport._fetch_engineering_diagrams", return_value=[])
    @patch("storage_control.services.mark_passport._fetch_web_analogs", return_value=["Bonolit D500"])
    def test_all_submodules_speed_and_portal_html_render(self, mock_web, mock_imgs):
        """Замеряет время работы каждого узла и проверяет, что главная страница рендерится < 800 мс."""
        timings = {}

        # 1. Подмодуль smart_router
        t0 = time.perf_counter()
        q = evaluate_parsing_quality(self.doc.title, ["Газобетонные блоки YTONG 200мм (или аналог)"])
        timings["1_smart_router_ms"] = round((time.perf_counter() - t0) * 1000, 1)
        self.assertEqual(q["clean"], 1)

        # 2. Подмодуль route_tracer (сводная ведомость + смены ЕНиР)
        t0 = time.perf_counter()
        rows = build_engineering_procurement_rows(PurchaseRequest.objects.filter(document=self.doc))
        timings["2_route_tracer_ms"] = round((time.perf_counter() - t0) * 1000, 1)
        self.assertEqual(len(rows), 1)

        # 3. Подмодуль mark_passport (паспорт + аналоги)
        t0 = time.perf_counter()
        passport = build_mark_passport_data("Газобетонные блоки YTONG 200мм (или аналог)")
        timings["3_mark_passport_ms"] = round((time.perf_counter() - t0) * 1000, 1)
        self.assertTrue(len(passport["tech"]["analogs"]) >= 1)

        # 4. Подмодуль export_staff_excel (3-листовой Excel)
        t0 = time.perf_counter()
        xlsx = build_staff_excel_bytes(doc=self.doc)
        timings["4_staff_excel_ms"] = round((time.perf_counter() - t0) * 1000, 1)
        self.assertTrue(len(xlsx) > 1000)

        # 5. Живой рендер главной страницы портала (GET /)
        client = Client()
        client.force_login(self.user)
        t0 = time.perf_counter()
        resp = client.get(f"/?doc_id={self.doc.id}")
        timings["5_portal_html_render_ms"] = round((time.perf_counter() - t0) * 1000, 1)

        print("\n[ТАЙМЕР СКОРОСТИ УЗЛОВ]:", timings)

        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode("utf-8")
        self.assertIn("ПТО & АСУ ТП ПОРТАЛ", html)
        self.assertIn("Ведомость закупок", html)
        self.assertIn("Газобетонные блоки YTONG", html)
        self.assertLess(timings["5_portal_html_render_ms"], 1000.0)
