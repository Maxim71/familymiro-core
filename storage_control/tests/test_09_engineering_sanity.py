import json
from django.test import TestCase, Client
from storage_control.models import Document, PurchaseRequest
from storage_control.services.input_calibrator import (
    classify_pdf_line_at_gate,
    assign_words_to_gost_columns,
)


class EngineeringSanityAuditTests(TestCase):
    def setUp(self):
        self.doc = Document.objects.create(title="23-24.0454-Р-КМ2.pdf")
        PurchaseRequest.objects.create(document=self.doc, material_name="Техноэласт ПЛАМЯ СТОП (или эквивалент)", required_qty=47.0, deficit_qty=47.0, unit="м²")
        PurchaseRequest.objects.create(document=self.doc, material_name="Техноэласт АКУСТИК СБ 350", required_qty=120.0, deficit_qty=120.0, unit="м²")
        PurchaseRequest.objects.create(document=self.doc, material_name="Арматура Ø12 А500С ГОСТ 34028-2016", required_qty=1450.0, deficit_qty=1450.0, unit="кг")
        PurchaseRequest.objects.create(document=self.doc, material_name="Фланец стальной Ду", required_qty=10.0, deficit_qty=10.0, unit="шт")
        PurchaseRequest.objects.create(document=self.doc, material_name="Фланец стальной Ду 50", required_qty=5.0, deficit_qty=5.0, unit="шт.")

    def test_01_roofing_no_du_tag_and_exact_and_match(self):
        data = json.loads(Client().get("/api/project-totals/", {"q": "Техноэласт ПЛАМЯ СТОП"}).content)
        self.assertEqual(len(data["items"]), 1)
        self.assertNotIn("Ду 25", data["items"][0]["mark_name"])

    def test_02_rebar_in_kg_and_tons_only(self):
        data = json.loads(Client().get("/api/project-totals/", {"q": "А500С"}).content)
        self.assertEqual(data["totals_by_unit"].get("т (тонн)"), 1.45)
        self.assertNotIn("м", data["totals_by_unit"])

    def test_03_dn100_du100_merge_and_missing_du_blocked(self):
        PurchaseRequest.objects.create(document=self.doc, material_name="Кран шаровой DN100", required_qty=3.0, deficit_qty=3.0, unit="шт")
        PurchaseRequest.objects.create(document=self.doc, material_name="Кран шаровой Ду 100", required_qty=4.0, deficit_qty=4.0, unit="шт.")
        d_kran = json.loads(Client().get("/api/project-totals/", {"q": "Кран шаровой"}).content)
        self.assertEqual(d_kran["items"][0]["qty"], 7.0)
        d_fl = json.loads(Client().get("/api/project-totals/", {"q": "Фланец"}).content)
        self.assertEqual(d_fl["totals_by_unit"].get("шт."), 5.0)
        self.assertEqual(len(d_fl["blocked_items"]), 1)

    def test_04_gate_classifier_and_xy_gost_column_extractor(self):
        self.assertEqual(classify_pdf_line_at_gate("2 3 4 5 Экспликация 1 этаж"), "STAMP_NOISE")
        self.assertEqual(classify_pdf_line_at_gate("материал обладает массой 6,3 кг"), "DESIGN_NOTE")
        words = [
            {"text": "1.1", "x": 50, "y": 500},
            {"text": "Техноэласт ПЛАМЯ СТОП (6.3 кг/м2)", "x": 220, "y": 500},
            {"text": "м²", "x": 760, "y": 500},
            {"text": "47", "x": 840, "y": 500},
        ]
        rows = assign_words_to_gost_columns(words, 1000.0)
        self.assertEqual(rows[0]["qty"], 47.0)
        self.assertEqual(rows[0]["unit"], "м²")
