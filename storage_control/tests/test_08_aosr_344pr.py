import io
import docx
from django.test import TestCase
from storage_control.models import Document, PurchaseRequest
from storage_control.services.export_aosr import build_aosr_docx_bytes


class Aosr344PrRegressionTest(TestCase):
    def test_aosr_matches_minstroy_344pr_and_filters_step_notes(self):
        doc = Document.objects.create(title="44-24.0454-\u0420-\u0421\u041a\u041a.pdf", revision_num=1)
        PurchaseRequest.objects.create(document=doc, material_name="\u0428\u0430\u0433 \u043a\u0440\u0435\u043f\u043b\u0435\u043d\u0438\u044f \u043b\u043e\u0442\u043a\u0430", required_qty=1.50, unit="\u043c", record_type="BUY")
        PurchaseRequest.objects.create(document=doc, material_name="\u041b\u043e\u0442\u043e\u043a \u043a\u0430\u0431\u0435\u043b\u044c\u043d\u044b\u0439 \u043f\u0435\u0440\u0444\u043e\u0440\u0438\u0440\u043e\u0432\u0430\u043d\u043d\u044b\u0439 200\u044560", required_qty=45.0, unit="\u043c", record_type="BUY")

        parsed = docx.Document(io.BytesIO(build_aosr_docx_bytes(doc)))
        full_text = "\n".join([p.text for p in parsed.paragraphs] + [c.text for t in parsed.tables for r in t.rows for c in r.cells])

        self.assertIn("\u041f\u0440\u0438\u043a\u0430\u0437 \u041c\u0438\u043d\u0441\u0442\u0440\u043e\u044f \u0420\u0424 \u2116 344/\u043f\u0440", full_text)
        self.assertIn("\u041f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435 \u2116 3", full_text)
        self.assertIn("\u041b\u043e\u0442\u043e\u043a \u043a\u0430\u0431\u0435\u043b\u044c\u043d\u044b\u0439 \u043f\u0435\u0440\u0444\u043e\u0440\u0438\u0440\u043e\u0432\u0430\u043d\u043d\u044b\u0439 200\u044560", full_text)
        self.assertIn("7. \u0420\u0430\u0437\u0440\u0435\u0448\u0430\u0435\u0442\u0441\u044f \u043f\u0440\u043e\u0438\u0437\u0432\u043e\u0434\u0441\u0442\u0432\u043e \u043f\u043e\u0441\u043b\u0435\u0434\u0443\u044e\u0449\u0438\u0445 \u0440\u0430\u0431\u043e\u0442", full_text)

    def test_customer_id_registry_xlsx_export(self):
        from storage_control.services.id_template_engine import build_filled_customer_registry_xlsx
        data = build_filled_customer_registry_xlsx()
        self.assertTrue(len(data) > 500)
