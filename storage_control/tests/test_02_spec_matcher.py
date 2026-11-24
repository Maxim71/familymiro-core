# -*- coding: utf-8 -*-
from decimal import Decimal
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from storage_control.models import Document, ParsedPage, WarehouseTmc, PurchaseRequest
from storage_control.services.spec_matcher import parse_specifications_and_create_requests


class Node02SpecMatcherTest(TestCase):
    """Отмашка №2: Парсинг спецификаций из PDF, сверка со складом и расчёт дефицита."""

    def setUp(self):
        WarehouseTmc.objects.all().delete()
        WarehouseTmc.objects.create(
            item_code="01-ГП",
            nomenclature="Геотекстиль Дорнит 300",
            unit="м2",
            stock_balance=Decimal("500.00"),
        )
        WarehouseTmc.objects.create(
            item_code="02-АВ",
            nomenclature="Датчик давления Danfoss",
            unit="шт",
            stock_balance=Decimal("20.00"),
        )

    def test_parse_multiple_spec_lines_and_calculate_deficit(self):
        """Спецификация с несколькими позициями корректно считает остатки и дефицит."""
        dummy_pdf = SimpleUploadedFile("spec_tom.pdf", b"%PDF-1.4\n%%EOF", content_type="application/pdf")
        doc = Document.objects.create(title="spec_tom.pdf", file=dummy_pdf)

        ParsedPage.objects.create(
            document=doc,
            page_number=1,
            text=(
                "1. Геотекстиль Дорнит 300 | м2 | 650.0\n"
                "2. Датчик давления Danfoss | 15 | шт\n"
                "3. Кабель ВВГнг-LS 3х2.5 1200 м\n"
            ),
        )

        result = parse_specifications_and_create_requests(doc)

        self.assertEqual(result["total_positions"], 3)
        self.assertGreaterEqual(result["covered_by_stock"], 1)
        self.assertGreaterEqual(result["requests_created"], 1)

        self.assertTrue(PurchaseRequest.objects.filter(document=doc).exists())
        
        

        cable_req = PurchaseRequest.objects.get(document=doc, material_name__icontains="Кабель")
        self.assertEqual(cable_req.deficit_qty, Decimal("1200.00"))
    def test_parse_genplan_roads_and_multiline_cables(self):
        """Отмашка №11: Таблица проездов/тротуаров (h, S, V) и многострочные выноски кабелей L=2x..."""
        dummy_pdf = SimpleUploadedFile("01-24.0454-Р-ГП.pdf", b"%PDF-1.4\n%%EOF", content_type="application/pdf")
        doc = Document.objects.create(title="01-24.0454-Р-ГП.pdf", file=dummy_pdf)

        ParsedPage.objects.create(
            document=doc,
            page_number=9,
            text=(
                "ВЕДОМОСТǥ ПРОЕЗДОВ, ТРОТУАРОВ, ДОРОЖЕК\n"
                "№п. п Наименование h, м S, м² V,м³ Тип Обозн. Прим.\n"
                "1 Проезд с асфальтобетонным покрытием 0,15 1 240,5 186,08 Тип 1\n"
                "2 Тротуар из тротуарной плитки 0,06 380,0 22,80 Тип 2\n"
                "4 АПвБШвнг(А)-LS-1 5х185\n"
                "L=2x107м (ввод 2)\n"
                "L=2x113м (ввод 3)\n"
                "ПвБШвнг(А)-LS-1 5х150\n"
                "L = 347м (от ДГУ до ШС-ЦОД)\n"
                "Примечания: 1. Система координат - МСК-71. 2. ЗУ-2, S=4 701 м2\n"
            ),
        )

        result = parse_specifications_and_create_requests(doc)
        reqs = list(PurchaseRequest.objects.filter(document=doc))
        materials_text = " | ".join(r.material_name for r in reqs)

        self.assertGreaterEqual(result["total_positions"], 3)
        self.assertIn("Проезд с асфальтобетонным покрытием", materials_text)
        self.assertIn("Тротуар из тротуарной плитки", materials_text)
        self.assertTrue(any(r.required_qty == Decimal("1240.50") for r in reqs))
        self.assertTrue(any(r.required_qty == Decimal("380.00") for r in reqs))
        self.assertTrue(any(r.required_qty in (Decimal("440.00"), Decimal("214.00"), Decimal("347.00")) for r in reqs))
        self.assertNotIn("МСК-71", materials_text)
        self.assertNotIn("ЗУ-2", materials_text)

    def test_separate_demolition_footnotes_from_new_purchase(self):
        """Отмашка №12: Сноски (*) и демонтаж бортового камня идут в работы (TEP), а не в закупку нового камня (BUY)."""
        dummy_pdf = SimpleUploadedFile("01-24.0454-Р-ГП-demo.pdf", b"%PDF-1.4\n%%EOF", content_type="application/pdf")
        doc = Document.objects.create(title="01-24.0454-Р-ГП-demo.pdf", file=dummy_pdf)

        ParsedPage.objects.create(
            document=doc,
            page_number=4,
            text=(
                "Бордюр дорожный БР 100.30.15 — 380 м\n"
                "* Демонтаж существующего бортового камня — 145 м\n"
                "* Разборка существующего асфальтобетонного покрытия — 320 м2\n"
            ),
        )

        parse_specifications_and_create_requests(doc)
        buy_items = list(PurchaseRequest.objects.filter(document=doc, record_type='BUY'))
        work_items = list(PurchaseRequest.objects.filter(document=doc, record_type='TEP'))

        self.assertEqual(len(buy_items), 1)
        self.assertIn("Бордюр дорожный", buy_items[0].material_name)
        self.assertEqual(buy_items[0].required_qty, Decimal("380.00"))

        self.assertEqual(len(work_items), 2)
        work_text = " | ".join(w.material_name for w in work_items)
        self.assertIn("Демонтаж", work_text)
        self.assertIn("Разборка", work_text)






