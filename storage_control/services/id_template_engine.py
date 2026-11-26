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
