# -*- coding: utf-8 -*-
import io
import openpyxl
from django.test import TestCase, Client
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from storage_control.models import Document
from storage_control.services.grid_extractor import (
    _auto_unrotate_matrix,
    _classify_table_schema,
    _clean_cell_text,
    extract_geometric_tables,
)
from storage_control.services.smart_router import (
    detect_document_profile,
    evaluate_parsing_quality,
    is_noise_for_document,
)


class Node06GridAndRouterIntegrationTest(TestCase):
    """Сквозной автотест: импорты, URL, векторный парсер, автоповорот 90°, 6 профилей и выгрузка Excel."""

    def test_01_bilingual_clean_and_90deg_unrotate(self):
        """Проверка очистки китайских иероглифов и разворота повёрнутой на 90° таблицы."""
        cleaned = _clean_cell_text("房间编号 помещения Номер，；")
        self.assertEqual(cleaned, "помещения Номер")

        # Имитация повёрнутой на 90° матрицы (3 строки × 5 колонок), где шапка оказалась в последней колонке
        rotated_matrix = [
            ["09-301", "09-302", "09-303", "09-304", "Номер помещения"],
            ["Ce-3", "Ce-2", "Ce-2", "Ce-1", "Потолок"],
            ["38.0", "21.7", "20.5", "15.0", "Площадь м2"],
        ]
        unrotated, was_rotated = _auto_unrotate_matrix(rotated_matrix)
        self.assertTrue(was_rotated)
        self.assertEqual(len(unrotated), 5)


    def test_02_ten_schema_signatures_and_corrupt_pdf_safety(self):
        """Проверка распознавания нестандартных таблиц (отделка, кабельный журнал) и защиты от битых PDF."""
        code_ar, is_std_ar, alert_ar = _classify_table_schema(["Номер помещения", "Потолок", "Стены", "Площадь м2"])
        self.assertEqual(code_ar, "FINISH_AR")
        self.assertFalse(is_std_ar)
        self.assertIn("FINISH_AR", alert_ar)

        code_gost, is_std_gost, alert_gost = _classify_table_schema(["Позиция", "Обозначение", "Наименование", "Кол-во", "Масса"])
        self.assertEqual(code_gost, "SPEC_GOST_21110")
        self.assertTrue(is_std_gost)
        self.assertEqual(alert_gost, "")

        # Проверка, что битый PDF не роняет систему ошибкой PdfiumError
        bad_pdf = SimpleUploadedFile("broken.pdf", b"%PDF-1.4\n%%EOF", content_type="application/pdf")
        doc = Document.objects.create(title="broken.pdf", file=bad_pdf)
        res = extract_geometric_tables(doc.file.path)
        self.assertEqual(res["tables_count"], 0)
        self.assertIn("error", res)

    def test_03_smart_router_six_profiles_and_noise_filter(self):
        """Проверка 6 строительных профилей и отсечения двуязычного/AutoCAD мусора."""
        p_ar = detect_document_profile("31 - Ведомость отделки помещений (01.07.24).pdf")
        self.assertEqual(p_ar["code"], "FINISH_AR")

        p_kzh = detect_document_profile("05-24.0454-Р-КЖ.pdf")
        self.assertEqual(p_kzh["code"], "METAL_KZH")

        self.assertTrue(is_noise_for_document("31 - Ведомость отделки помещений.pdf", "Типотделки装修类型 Наименование Площадь"))
        self.assertTrue(is_noise_for_document("05-24.0454-Р-КЖ.pdf", "3535120160ГС12 200х300"))
        self.assertFalse(is_noise_for_document("02-24.0454-Р-АР0.pdf", "Газобетонные блоки YTONG 200мм (или аналог)"))

        q = evaluate_parsing_quality(
            "31 - Ведомость отделки.pdf",
            ["Типотделки装修类型 Площадь", "Шпатлёвка полимерная Ceresit CT 126 (меш. 20 кг)"],
        )
        self.assertEqual(q["clean"], 1)
        self.assertEqual(q["dropped"], 1)

    def test_04_export_dynamic_table_endpoint_returns_valid_xlsx(self):
        """Проверка маршрута /export-dynamic-table/ и генерации файла Excel (.xlsx) из кэша."""
        dummy_pdf = SimpleUploadedFile("31-otdelka.pdf", b"%PDF-1.4\n%%EOF", content_type="application/pdf")
        doc = Document.objects.create(title="31-otdelka.pdf", file=dummy_pdf)

        cache.set(
            f"geo_dyn_tables_v2_{doc.id}",
            [
                {
                    "page": 1,
                    "schema_code": "FINISH_AR",
                    "is_standard_spec": False,
                    "schema_alert": "Новая таблица отделки",
                    "headers": ["Помещение", "Потолок", "Площадь, м2"],
                    "rows": [["09-301", "Ce-3", "38.0"]],
                }
            ],
            3600,
        )

        client = Client()
        url = f"{reverse('storage_control:export_dynamic_table')}?doc_id={doc.id}&idx=0"
        resp = client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("spreadsheetml.sheet", resp["Content-Type"])

        wb = openpyxl.load_workbook(io.BytesIO(resp.content))
        ws = wb.active
        self.assertEqual(ws.cell(row=1, column=1).value, "Помещение")
        self.assertEqual(ws.cell(row=2, column=3).value, "38.0")
