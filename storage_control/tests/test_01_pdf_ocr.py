# -*- coding: utf-8 -*-
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from storage_control.models import Document, ParsedPage
from storage_control.services.pdf_ocr import extract_and_store_pages


def _create_vector_pdf_bytes(text: str = "24.0454-P-GP Geotextile Dornit 300 650 m2") -> bytes:
    """Генерирует валидный минимальный векторный PDF на чистом Python без внешних библиотек."""
    stream = f"BT /F1 14 Tf 50 750 Td ({text}) Tj ET".encode("latin-1")
    objs = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n",
        f"4 0 obj\n<< /Length {len(stream)} >>\nstream\n".encode("latin-1") + stream + b"\nendstream\nendobj\n",
        b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = []
    for obj in objs:
        offsets.append(len(pdf))
        pdf.extend(obj)
    xref_pos = len(pdf)
    pdf.extend(f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode("latin-1"))
    for off in offsets:
        pdf.extend(f"{off:010d} 00000 n \n".encode("latin-1"))
    pdf.extend(
        f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode("latin-1")
    )
    return bytes(pdf)


class Node01PdfOcrRelayTest(TestCase):
    """Отмашка №1: Проверка лёгкого векторного конвейера и защиты от битых файлов."""

    def test_valid_pdf_extract_and_cache(self):
        """Валидный векторный PDF разбирается без внешних DLL и сохраняется в ParsedPage."""
        pdf_bytes = _create_vector_pdf_bytes("24.0454-P-GP Geotextile Dornit 300 650 m2")
        uploaded = SimpleUploadedFile("node01_valid.pdf", pdf_bytes, content_type="application/pdf")
        doc = Document.objects.create(title="node01_valid.pdf", file=uploaded)

        report = extract_and_store_pages(doc)

        self.assertEqual(report["errors"], [])
        self.assertEqual(report["pages_processed"], 1)

        cached_page = ParsedPage.objects.filter(document=doc, page_number=1).first()
        self.assertIsNotNone(cached_page)
        self.assertIn("Dornit 300", cached_page.text)

    def test_corrupted_pdf_graceful_os_protection(self):
        """Битый PDF не роняет сервер, а возвращает понятную ошибку в report['errors']."""
        broken_file = SimpleUploadedFile("broken.pdf", b"%PDF-1.4_BROKEN_NO_EOF", content_type="application/pdf")
        doc = Document.objects.create(title="broken.pdf", file=broken_file)

        report = extract_and_store_pages(doc)

        self.assertEqual(report["pages_processed"], 0)
        self.assertTrue(len(report["errors"]) > 0)
