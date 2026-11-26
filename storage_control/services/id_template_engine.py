import os
import re
import zipfile
import xml.etree.ElementTree as ET


def extract_text_from_docx(docx_path: str) -> str:
    if not docx_path or not os.path.exists(docx_path):
        return ""
    try:
        with zipfile.ZipFile(docx_path) as zf:
            xml_bytes = zf.read("word/document.xml")
        root = ET.fromstring(xml_bytes)
        paragraphs = []
        for p in root.iter():
            if p.tag.endswith("}p"):
                texts = [t.text for t in p.iter() if t.tag.endswith("}t") and t.text]
                if texts:
                    paragraphs.append("".join(texts))
        return "\n".join(paragraphs)
    except Exception:
        return ""


def parse_id_memo_and_template(file_path: str) -> dict:
    """
    ????????? ??????? ?? ???????? ?? (.docx / .txt / .xlsx) ??? ????? ??????:
    ?????????? ?????????? ?????????, ???????????? ?????????? ????????? ? ????????? ???????.
    """
    ext = os.path.splitext(file_path)[1].lower()
    raw_text = ""
    excel_headers = []

    if ext == ".docx":
        raw_text = extract_text_from_docx(file_path)
    elif ext in (".txt", ".md", ".csv"):
        raw_text = open(file_path, encoding="utf-8", errors="ignore").read()
    elif ext in (".xlsx", ".xlsm"):
        try:
            import openpyxl
            wb = openpyxl.load_workbook(file_path, data_only=True)
            for ws in wb.worksheets[:3]:
                for r_idx in range(1, min(15, ws.max_row + 1)):
                    row_vals = [str(ws.cell(r_idx, c).value).strip() for c in range(1, min(20, ws.max_column + 1)) if ws.cell(r_idx, c).value is not None]
                    if len(row_vals) >= 3 and not excel_headers:
                        excel_headers = row_vals
                    if row_vals:
                        raw_text += " | ".join(row_vals) + "\n"
        except Exception as e:
            raw_text = f"Excel read error: {e}"

    low = raw_text.lower()
    # ?????????? ?????????????: ??? ??? ? ??? ????
    if any(k in low for k in ("\u043f\u0430\u043c\u044f\u0442\u043a", "\u043f\u0435\u0440\u0435\u0434\u0430\u0447\u0430 \u0438\u0434", "\u0440\u0435\u0435\u0441\u0442\u0440 \u0438\u0441\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u044c\u043d", "\u0433\u043e\u0441\u0442 \u0440 70108")):
        doc_purpose = "\u041f\u0430\u043c\u044f\u0442\u043a\u0430 / \u0420егламент передачи ИД (для ГАСН и Стройконтроля)"
    elif any(k in low for k in ("\u0430\u043e\u0441\u0440", "\u0441\u043a\u0440\u044b\u0442\u044b\u0445 \u0440\u0430\u0431\u043e\u0442", "344/\u043f\u0440")):
        doc_purpose = "\u0428аблон АОСР (Приказ Минстроя № 344/пр)"
    elif any(k in low for k in ("\u043a\u0441-2", "\u043a\u0441-3", "\u043c-29", "\u0441писание \u043cатериал")):
        doc_purpose = "\u0412едомость закрытия объёмов КС-2 / М-29 (для Заказчика и ФНС)"
    elif excel_headers:
        doc_purpose = "\u0422абличный шаблон / Ведомость ТМЦ для авто-заполнения"
    else:
        doc_purpose = "\u0421опроводительный документ / Пачка листов ИД"

    rules = [
        re.sub(r'\s+', ' ', ln).strip()
        for ln in raw_text.splitlines()
        if len(ln.strip()) >= 12 and any(w in ln.lower() for w in ("\u043eбязат", "\u043fодпис", "\u0441ертифик", "\u043fаспорт", "\u0440еестр", "\u0430оср", "\u0441хем", "\u043fечат"))
    ][:12]

    return {
        "ok": True,
        "file_name": os.path.basename(file_path),
        "doc_purpose": doc_purpose,
        "excel_headers": excel_headers,
        "extracted_rules": rules,
        "text_preview": raw_text[:800],
    }


def get_saved_object_passport() -> dict:
    import os, json
    from django.conf import settings
    fpath = os.path.join(settings.BASE_DIR, "object_passport.json")
    defaults = {
        "object_name": "\u0426\u041e\u0414 \u041d\u041f\u041e \u00ab\u0421\u041f\u041b\u0410\u0412\u00bb (\u0433. \u0422\u0443\u043b\u0430)",
        "axes_info": "\u041e\u0441\u0438 1\u201317 / \u0410\u2013\u0416 (\u0448\u0430\u0433 6000 \u043c\u043c)",
        "floors_info": "5 \u044d\u0442\u0430\u0436\u0435\u0439 + \u043f\u043e\u0434\u0432\u0430\u043b (-3,640 \u2192 +16,800 \u043c)",
        "dimensions_info": "\u0414\u043b\u0438\u043d\u0430 96,0 \u043c \u00b7 \u0428\u0438р\u0438\u043d\u0430 36,0 \u043c",
        "developer_info": "\u0417\u0430\u0441\u0442\u0440\u043e\u0439\u0449\u0438\u043a / \u0422\u0435\u0445\u0437\u0430\u043a\u0430\u0437\u0447\u0438\u043a (\u041e\u0413\u0420\u041d, \u0418\u041d\u041d, \u0421\u0420\u041e)",
        "builder_info": "\u0413\u0435\u043d\u043f\u043e\u0434\u0440я\u0434\u0447и\u043a (\u041e\u0413\u0420\u041d, \u0418\u041d\u041d, \u0421\u0420\u041e)",
        "designer_info": "\u041f\u0440\u043e\u0435\u043a\u0442\u0438\u0440\u043e\u0432\u0449\u0438\u043a (\u041e\u0413\u0420\u041d, \u0418\u041d\u041d, \u0421\u0420\u041e)",
        "subcontractor_info": "\u0421\u0443\u0431\u043f\u043e\u0434\u0440\u044f\u0434\u0447\u0438\u043a",
        "nrs_inspector": "",
        "nrs_executor": "",
    }
    if os.path.exists(fpath):
        try:
            saved = json.load(open(fpath, encoding="utf-8"))
            defaults.update({k: v for k, v in saved.items() if v})
        except Exception:
            pass
    return defaults


def save_object_passport(data: dict) -> dict:
    import os, json
    from django.conf import settings
    cur = get_saved_object_passport()
    cur.update({k: str(v).strip() for k, v in data.items() if v is not None})
    fpath = os.path.join(settings.BASE_DIR, "object_passport.json")
    json.dump(cur, open(fpath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return cur


def build_filled_customer_registry_xlsx(template_bytes: bytes | None = None, memo_text: str = "") -> bytes:
    """
    ????????? ?????? ??????? ?? ????????? (.xlsx) ????????? ??????????? ? ?????? ?? ????
    ??? ??????? ????????? ?????? ?? ?? ??????? ???????? ?? ? 344/??.
    """
    import io
    import openpyxl
    from django.utils import timezone
    from storage_control.models import Document, StockMovement
    from storage_control.services.id_template_engine import get_saved_object_passport

    op = get_saved_object_passport()
    today_str = timezone.localdate().strftime("%d.%m.%Y")

    # ???????? ???????? ?????? ??????? ?? ?? ????
    rows_data = []
    idx = 1
    for doc in Document.objects.order_by("id")[:40]:
        rows_data.append((
            idx,
            f"\u0410\u043a\u0442 \u043e\u0441\u0432\u0438\u0434\u0435\u0442\u0435\u043b\u044c\u0441\u0442\u0432\u043e\u0432\u0430\u043d\u0438\u044f \u0441\u043a\u0440\u044b\u0442\u044b\u0445 \u0440\u0430\u0431\u043e\u0442 (\u041f\u0440\u0438\u043a\u0430\u0437 \u2116 344/\u043f\u0440) \u043f\u043e \u043a\u043e\u043c\u043f\u043b\u0435\u043a\u0442\u0443 {doc.title}",
            f"\u2116 {idx}-\u0410\u041e\u0421\u0420 \u043e\u0442 {today_str}",
            doc.title,
            4,
            "\u041f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435 \u2116 3 (\u044d\u043a\u0437. 1\u20134)",
        ))
        idx += 1

    for mv in StockMovement.objects.order_by("-id")[:25]:
        rows_data.append((
            idx,
            f"{mv.get_movement_kind_display()}: {mv.material_name} ({mv.qty} {mv.unit})",
            f"\u2116 {mv.id} \u043e\u0442 {today_str}",
            mv.axes_and_ojr or op.get("axes_info", ""),
            2,
            mv.brigade_or_subcontractor or "\u041f\u0430\u0441\u043f\u043e\u0440\u0442\u0430 \u0438 \u0441\u0435\u0440\u0442\u0438\u0444\u0438\u043a\u0430\u0442\u044b \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u044b",
        ))
        idx += 1

    if not rows_data:
        rows_data.append((1, "\u0410\u043a\u0442 \u043e\u0441\u0432\u0438\u0434\u0435\u0442\u0435\u043b\u044c\u0441\u0442\u0432\u043e\u0432\u0430\u043d\u0438\u044f \u0441\u043a\u0440\u044b\u0442\u044b\u0445 \u0440\u0430\u0431\u043e\u0442 (\u041f\u0440\u0438\u043a\u0430\u0437 \u2116 344/\u043f\u0440)", f"\u2116 1-\u0410\u041e\u0421\u0420 \u043e\u0442 {today_str}", op.get("axes_info", ""), 4, "\u0413\u043e\u0442\u043e\u0432\u043e \u043a \u043f\u0435\u0440\u0435\u0434\u0430\u0447\u0435 \u0421\u041a"))

    if template_bytes:
        wb = openpyxl.load_workbook(io.BytesIO(template_bytes))
        ws = wb.active
        start_row = ws.max_row + 1
        for r_off, row_vals in enumerate(rows_data):
            for c_idx, val in enumerate(row_vals, start=1):
                ws.cell(row=start_row + r_off, column=c_idx, value=val)
    else:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "\u0420\u0435\u0435\u0441\u0442\u0440_\u0418\u0414_344\u043f\u0440"
        ws.append([f"\u0420\u0415\u0415\u0421\u0422\u0420 \u0418\u0421\u041f\u041e\u041b\u041d\u0418\u0422\u0415\u041b\u042c\u041d\u041e\u0419 \u0414\u041e\u041a\u0423\u041c\u0415\u041d\u0422\u0410\u0426\u0418\u0418 \u2014 {op.get('object_name', '')}"])
        ws.append([
            "\u2116 \u043f/\u043f",
            "\u041d\u0430\u0438\u043c\u0435\u043d\u043e\u0432\u0430\u043d\u0438\u0435 \u0434\u043e\u043a\u0443\u043c\u0435\u043d\u0442\u0430 (\u041f\u0440\u0438\u043a\u0430\u0437 \u041c\u0438\u043d\u0441\u0442\u0440\u043e\u044f \u0420\u0424 \u2116 344/\u043f\u0440)",
            "\u041d\u043e\u043c\u0435\u0440 \u0438 \u0434\u0430\u0442\u0430",
            "\u0420\u0430\u0437\u0434\u0435\u043b \u0420\u0414 / \u041e\u0441\u0438",
            "\u041a\u043e\u043b-\u0432\u043e \u043b\u0438\u0441\u0442\u043e\u0432",
            "\u041f\u0440\u0438\u043c\u0435\u0447\u0430\u043d\u0438\u0435",
        ])
        for row_vals in rows_data:
            ws.append(list(row_vals))

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()
