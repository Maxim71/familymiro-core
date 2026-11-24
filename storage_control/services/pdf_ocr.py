# -*- coding: utf-8 -*-
import io
import os
import logging
from pypdf import PdfReader
from storage_control.models import ParsedPage
from storage_control.services.layout_analyzer import analyze_zones
from storage_control.services.table_extractor import extract_tables_and_words
from storage_control.services.vector_raster_gate import read_vector_or_raster
from storage_control.services.revision_tracer import trace_revision_diff
from storage_control.services.engineering_extractor import EngineeringDataExtractor
from storage_control.services.automation_macro import AutomationAndHydraulicsMacro

logger = logging.getLogger(__name__)

# Безопасная загрузка PyMuPDF (fitz) с резервным переключением на pypdfium2
try:
    import fitz
    HAS_FITZ = True
except ImportError as dll_err:
    logger.warning("PyMuPDF (fitz) недоступен в ОС (%s), используем pypdfium2 + pypdf", dll_err)
    HAS_FITZ = False
    import pypdfium2 as pdfium


def render_page_png(doc, page_number: int, dpi: int = 150) -> bytes:
    """Рендерит страницу PDF в PNG через fitz или резервный pypdfium2."""
    if not doc.file or not os.path.exists(doc.file.path):
        return b""
    try:
        if HAS_FITZ:
            with fitz.open(doc.file.path) as pdf:
                if page_number < 1 or page_number > len(pdf):
                    return b""
                return pdf[page_number - 1].get_pixmap(dpi=dpi).tobytes("png")
        else:
            pdf = pdfium.PdfDocument(doc.file.path)
            if page_number < 1 or page_number > len(pdf):
                return b""
            page = pdf[page_number - 1]
            bitmap = page.render(scale=dpi / 72.0)
            pil_image = bitmap.to_pil()
            buf = io.BytesIO()
            pil_image.save(buf, format="PNG")
            return buf.getvalue()
    except Exception as exc:
        logger.error("Ошибка рендера страницы %s (%s): %s", page_number, doc.title, exc)
        return b""


def extract_and_store_pages(doc) -> dict:
    """Главный конвейер разбора чертежей с автоматическим выбором PDF-движка ОС."""
    report = {
        "pages_processed": 0,
        "tables_rows": 0,
        "revisions_changed": 0,
        "total_io_signals": 0,
        "errors": [],
    }

    try:
        file_path = doc.file.path
        if not os.path.exists(file_path):
            report["errors"].append(f"Файл не найден на диске ОС: {doc.title}")
            return report
    except (ValueError, NotImplementedError, OSError) as os_err:
        report["errors"].append(f"Ошибка доступа к файлу в ОС: {os_err}")
        return report

    # Ветка 1: Если доступен PyMuPDF (fitz)
    if HAS_FITZ:
        try:
            pdf = fitz.open(file_path)
        except Exception as open_err:
            report["errors"].append(f"Не удалось открыть PDF: {open_err}")
            return report

        with pdf:
            for page_idx, page in enumerate(pdf, start=1):
                try:
                    zone_info = analyze_zones(page)
                    table_info = extract_tables_and_words(page)
                    report["tables_rows"] += len(table_info["table_rows"])

                    content_info = read_vector_or_raster(page)
                    full_text = content_info["text"]
                    if table_info["table_rows"]:
                        full_text += "\n--- ТАБЛИЦЫ СПЕЦИФИКАЦИИ ---\n" + "\n".join(table_info["table_rows"])

                    if not full_text.strip():
                        report["errors"].append(f"Стр. {page_idx}: пустой лист или нечитаемый скан.")
                        continue

                    _save_parsed_page(doc, page_idx, full_text, zone_info["stamp_code"], content_info["mode"], report)
                except Exception as page_err:
                    report["errors"].append(f"Стр. {page_idx}: ошибка разбора ({page_err})")
        return report

    # Ветка 2: Резервный конвейер на pypdf + pypdfium2 (работает без внешних DLL)
    try:
        reader = PdfReader(file_path)
        for page_idx, page in enumerate(reader.pages, start=1):
            full_text = (page.extract_text() or "").strip()
            mode = "ВЕКТОР (pypdf)"

            if len(full_text) < 15:
                from storage_control.services.vector_raster_gate import _get_ocr
                engine = _get_ocr()
                png_bytes = render_page_png(doc, page_idx, dpi=200)
                if engine and png_bytes:
                    res, _ = engine(png_bytes)
                    full_text = "\n".join(item[1] for item in (res or []) if len(item) > 1 and item[1])
                    mode = "РАСТР / OCR (pypdfium2)"

            if not full_text.strip():
                report["errors"].append(f"Стр. {page_idx}: пустой лист или нечитаемый скан.")
                continue

            _save_parsed_page(doc, page_idx, full_text, "", mode, report)
    except Exception as fallback_err:
        report["errors"].append(f"Ошибка разбора PDF: {fallback_err}")

    return report


def _save_parsed_page(doc, page_idx: int, full_text: str, stamp_code: str, mode: str, report: dict):
    """Общий блок сохранения страницы, трассировки ревизий и расчёта АСУ ТП."""
    diff_status = trace_revision_diff(doc, page_idx, full_text)
    if "Изменено" in diff_status or "Новый лист" in diff_status:
        report["revisions_changed"] += 1

    eng_data = EngineeringDataExtractor.analyze_text(full_text)
    macro_data = AutomationAndHydraulicsMacro.run_macro(full_text)
    report["total_io_signals"] += macro_data["total_io_signals"]

    axes_summary = " | ".join(filter(None, [
        f"Штамп: {stamp_code}" if stamp_code else "",
        eng_data.get("location_summary", ""),
        mode,
        diff_status,
    ]))[:100]

    k_com_summary = ""
    if macro_data["cabinets"] or macro_data["sensors"] or macro_data["hydraulics"]:
        cabs = ",".join(c["code"] for c in macro_data["cabinets"][:3]) or "КИПиА"
        k_com_summary = f"ШУ: {cabs} | Сигналов: {macro_data['total_io_signals']}"[:50]
    elif "уплотнен" in full_text.lower():
        k_com_summary = "К_упл в тексте"

    ParsedPage.objects.update_or_create(
        document=doc,
        page_number=page_idx,
        defaults={
            "text": full_text[:20000],
            "detected_axes": axes_summary,
            "detected_k_com": k_com_summary,
        },
    )
    report["pages_processed"] += 1
