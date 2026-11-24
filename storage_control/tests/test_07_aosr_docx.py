# -*- coding: utf-8 -*-
import io
from decimal import Decimal
import docx
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from storage_control.models import Document, PurchaseRequest


class Node07AosrDocxExportTest(TestCase):
    """Отмашка №7: Проверка генерации Акта освидетельствования скрытых работ (АОСР .docx)."""

    def setUp(self):
        f_kj = SimpleUploadedFile("09-24.0454-Р-КЖ0.1.pdf", b"%PDF-1.4\n%%EOF", content_type="application/pdf")
        self.doc = Document.objects.create(title="09-24.0454-Р-КЖ0.1.pdf", file=f_kj)
        PurchaseRequest.objects.create(
            document=self.doc,
            record_type="TEP",
            discipline="КЖ",
            floor_info="Котлован",
            material_name="Добор грунта вручную",
            unit="м3",
            required_qty=Decimal("467.00"),
        )

    def test_aosr_docx_contains_dates_people_and_volumes(self):
        client = Client()
        resp = client.get(reverse("storage_control:export_aosr"), {
            "doc_id": self.doc.id,
            "handover_mode": "SUB_TO_GEN",
            "date_start": "10.11.2026",
            "date_end": "15.11.2026",
            "executor_name": "Иванов И.И. (Прораб)",
            "inspector_name": "Косарев М.В. (ПТО)",
            "next_work": "Устройство бетонной подготовки B7.5",
        })
        self.assertEqual(resp.status_code, 200)
        self.assertIn("wordprocessingml.document", resp["Content-Type"])

        parsed_doc = docx.Document(io.BytesIO(resp.content))
        full_text = "\n".join(p.text for p in parsed_doc.paragraphs)
        self.assertIn("Субподрядчик → Генподрядчик", full_text)
        self.assertIn("10.11.2026", full_text)
        self.assertIn("15.11.2026", full_text)
        self.assertIn("Иванов И.И.", full_text)
        self.assertIn("бетонной подготовки B7.5", full_text)
