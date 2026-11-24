# -*- coding: utf-8 -*-
import difflib
from storage_control.models import Document, ParsedPage


def trace_revision_diff(doc, page_number: int, new_text: str) -> str:
    """Сравнивает лист с предыдущей загруженной версией того же тома и подсвечивает изменения."""
    prev_doc = (
        Document.objects.filter(title=doc.title)
        .exclude(id=doc.id)
        .order_by('-uploaded_at')
        .first()
    )
    if not prev_doc:
        return "Первичная ревизия"

    prev_page = ParsedPage.objects.filter(document=prev_doc, page_number=page_number).first()
    if not prev_page or not prev_page.text:
        return "Новый лист в ревизии"

    diff = list(difflib.unified_diff(prev_page.text.splitlines(), new_text.splitlines(), lineterm='', n=0))
    added = [line[1:].strip() for line in diff if line.startswith('+') and not line.startswith('+++')]

    if not added:
        return "Без изменений"
    return f"Изменено строк: {len(added)} ({'; '.join(added[:2])[:55]})"
