# -*- coding: utf-8 -*-
import os
import re
from PIL import Image, ImageOps, ImageStat, ImageFilter
from storage_control.models import PurchaseRequest

try:
    import cv2
    import numpy as np
    HAS_CV2 = True
except Exception:
    HAS_CV2 = False

try:
    import pytesseract
    HAS_TESSERACT = True
except Exception:
    HAS_TESSERACT = False

# Профили освещения и экспозиции для реальных условий съёмки
SCENE_PROFILES = {
    "OUTDOOR_SUN": {"label": "☀️ Улица / Яркое солнце", "gamma": 0.90, "clahe": 1.8, "sharpen": 1.2},
    "GARAGE_HANGAR": {"label": "🏚️ Гараж / Ангар / Сумерки", "gamma": 1.45, "clahe": 3.2, "sharpen": 1.6},
    "WAREHOUSE_INDOOR": {"label": "🏭 Помещение / Склад", "gamma": 1.15, "clahe": 2.4, "sharpen": 1.4},
    "CONSTRUCTION_SITE": {"label": "🏗️ Стройплощадка (пыль / печати)", "gamma": 1.25, "clahe": 2.8, "sharpen": 1.8},
}


def _detect_scene_profile(gray_np: "np.ndarray", requested_scene: str = "AUTO") -> tuple[str, dict]:
    """Автоматически определяет условия съёмки по яркости и контрасту кадра (или берёт выбранный профиль)."""
    if requested_scene in SCENE_PROFILES:
        return requested_scene, SCENE_PROFILES[requested_scene]

    mean_luma = float(np.mean(gray_np))
    std_luma = float(np.std(gray_np))
    if mean_luma < 95.0:
        code = "GARAGE_HANGAR"
    elif mean_luma > 185.0 and std_luma > 55.0:
        code = "OUTDOOR_SUN"
    elif std_luma < 42.0:
        code = "CONSTRUCTION_SITE"
    else:
        code = "WAREHOUSE_INDOOR"
    return code, SCENE_PROFILES[code]


def _enhance_black_white_and_autoframe(pil_img: Image.Image, scene_mode: str = "AUTO") -> tuple[Image.Image, dict]:
    """
    1) Автонаведение: находит контур листа документа и обрезает лишний фон;
    2) Калибровка точки чёрного и точки белого + CLAHE по профилю сцены;
    3) Микрорезкость (Unsharp Mask) для чёткого чтения OCR, QR и штрихкодов.
    """
    if not HAS_CV2:
        return pil_img, {"scene_code": "BASIC", "scene_label": "Базовый режим PIL", "auto_cropped": False}

    rgb = np.array(pil_img.convert("RGB"))
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    scene_code, cfg = _detect_scene_profile(gray, scene_mode)

    # 1. Автонаведение: поиск светлого листа документа и обрезка лишнего фона
    auto_cropped = False
    h, w = gray.shape
    blur = cv2.GaussianBlur(gray, (7, 7), 0)
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest = max(contours, key=cv2.contourArea)
        area_ratio = cv2.contourArea(largest) / float(w * h)
        if 0.25 <= area_ratio <= 0.92:
            x, y, cw, ch = cv2.boundingRect(largest)
            pad = 12
            x0, y0 = max(0, x - pad), max(0, y - pad)
            x1, y1 = min(w, x + cw + pad), min(h, y + ch + pad)
            bgr = bgr[y0:y1, x0:x1]
            auto_cropped = True

    # 2. Гамма-коррекция под выбранную сцену (Гараж / Улица / Склад / Стройка)
    inv_gamma = 1.0 / cfg["gamma"]
    lut = np.array([((i / 255.0) ** inv_gamma) * 255 for i in range(256)], dtype="uint8")
    bgr = cv2.LUT(bgr, lut)

    # Для стройплощадки используем красный канал (убирает синюю печать поверх цифр!)
    if scene_code == "CONSTRUCTION_SITE":
        work_gray = bgr[:, :, 2]
    else:
        lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
        l_chan, a_chan, b_chan = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=cfg["clahe"], tileGridSize=(8, 8))
        l_chan = clahe.apply(l_chan)
        work_gray = cv2.cvtColor(cv2.merge((l_chan, a_chan, b_chan)), cv2.COLOR_LAB2GRAY)

    # 3. Калибровка точки чёрного (4%) и точки белого (96%) -> чистый белый фон и чёрный шрифт
    p_low, p_high = np.percentile(work_gray, (4, 96))
    if p_high > p_low + 10:
        stretched = np.clip((work_gray.astype(np.float32) - p_low) * (255.0 / (p_high - p_low)), 0, 255).astype(np.uint8)
    else:
        stretched = work_gray

    # 4. Повышение резкости контуров (Unsharp Mask)
    gaussian = cv2.GaussianBlur(stretched, (0, 0), 2.0)
    sharp = cv2.addWeighted(stretched, 1.0 + cfg["sharpen"] * 0.5, gaussian, -cfg["sharpen"] * 0.5, 0)

    enhanced_pil = Image.fromarray(sharp).convert("RGB")
    return enhanced_pil, {
        "scene_code": scene_code,
        "scene_label": cfg["label"],
        "auto_cropped": auto_cropped,
        "bw_levels": f"Чёрный={int(p_low)} → 0, Белый={int(p_high)} → 255",
    }
def _calc_sharpness_pct(pil_img: Image.Image) -> float:
    gray = pil_img.convert("L").resize((800, 800))
    edges = gray.filter(ImageFilter.FIND_EDGES)
    stat = ImageStat.Stat(edges)
    std_val = float(sum(stat.stddev)) if stat.stddev else 0.0
    return round(min(100.0, (std_val / 45.0) * 100.0), 1)



def _decode_qr_and_barcodes(pil_img: Image.Image) -> list[dict]:
    results = []
    if not HAS_CV2:
        return results

    rgb = np.array(pil_img.convert("RGB"))
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

    qr_det = cv2.QRCodeDetector()
    try:
        retval, decoded_info, _, _ = qr_det.detectAndDecodeMulti(bgr)
        if retval and decoded_info:
            for txt in decoded_info:
                if txt and txt.strip():
                    results.append({"type": "QR_CODE", "raw": txt.strip(), "parsed": _parse_fns_qr(txt.strip())})
    except Exception:
        txt, _, _ = qr_det.detectAndDecode(bgr)
        if txt and txt.strip():
            results.append({"type": "QR_CODE", "raw": txt.strip(), "parsed": _parse_fns_qr(txt.strip())})

    try:
        bc_det = cv2.barcode.BarcodeDetector()
        ok, bc_info, bc_types, _ = bc_det.detectAndDecodeWithType(bgr)
        if ok and bc_info:
            for idx, code_val in enumerate(bc_info):
                if code_val and code_val.strip():
                    b_type = bc_types[idx] if bc_types and idx < len(bc_types) else "BARCODE"
                    results.append({"type": b_type, "raw": code_val.strip(), "parsed": {}})
    except Exception:
        pass

    return results


def _parse_fns_qr(qr_text: str) -> dict:
    parsed = {}
    m_inn = re.search(r'(?:inn|инн)[=:\s]*(\d{10,12})', qr_text, re.IGNORECASE)
    if m_inn:
        parsed["inn"] = m_inn.group(1)
    m_sum = re.search(r'(?:s|sum|сумма)[=:\s]*(\d+(?:[\.,]\d{2})?)', qr_text, re.IGNORECASE)
    if m_sum:
        parsed["sum"] = m_sum.group(1)
    m_date = re.search(r'(?:t|date|дата)[=:\s]*(\d{4}[\-\.]?\d{2}[\-\.]?\d{2})', qr_text, re.IGNORECASE)
    if m_date:
        parsed["date"] = m_date.group(1)
    m_doc = re.search(r'(?:n|num|документ)[=:\s]*([А-ЯЁA-Z0-9\-/]+)', qr_text, re.IGNORECASE)
    if m_doc:
        parsed["doc_num"] = m_doc.group(1)
    return parsed


def _extract_axes_and_elevation(text: str) -> tuple[str, str]:
    """Универсальный поиск осей (А-Г/1-5, QQ/1-TT/46-47/1, 1с-8с, ПК) и высотных отметок (-9.000, +4,200, У.Ч.П.)."""
    src = text or ""
    axes_patterns = (
        r'\b([А-ЯЁA-Z]{1,3}(?:/\d+|[а-яёa-z\'])?\s*[\-–]\s*[А-ЯЁA-Z]{1,3}(?:/\d+|[а-яёa-z\'])?\s*/\s*\d+(?:/\d+|[а-яёa-z\'])?\s*[\-–]\s*\d+(?:/\d+|[а-яёa-z\'])?)\b',
        r'(?:в\s+осях|по\s+ос[иям])\s+([А-ЯЁA-Z0-9/\-–\s]{2,28})',
        r'\b(ПК\s*\d+\+\d+(?:\s*[\-–]\s*ПК\s*\d+\+\d+)?)\b',
    )
    found_axes = ""
    for pat in axes_patterns:
        m = re.search(pat, src, re.IGNORECASE)
        if m:
            found_axes = m.group(1).strip(" .,;")
            break

    elev_patterns = (
        r'(?:отм\.?|у\.ч\.п\.?)\s*([\+\-]?\d{1,3}[\.,]\d{3})\b',
        r'([\+\-]\d{1,3}[\.,]\d{3})\b',
        r'\b(\d{1,2}\s*(?:этаж|ярус)|подвал|кровля|секция\s*\d+)\b',
    )
    found_elev = ""
    for pat in elev_patterns:
        m = re.search(pat, src, re.IGNORECASE)
        if m:
            found_elev = m.group(1).replace(",", ".").strip(" .,;")
            break

    return found_axes, found_elev



def analyze_field_photo(image_path: str, manual_hint_text: str = "", scene_mode: str = "AUTO") -> dict:
    """
    Главная функция «Зрения сокола» с адаптацией под условия съёмки (Улица / Гараж-Ангар / Склад / Стройка),
    автонаведением на лист и калибровкой чёрного/белого.
    """
    if not image_path or not os.path.exists(image_path):
        return {"ok": False, "error": "Файл изображения не найден"}

    raw_pil = ImageOps.exif_transpose(Image.open(image_path))
    sharpness_before = _calc_sharpness_pct(raw_pil)
    enhanced_pil, vision_meta = _enhance_black_white_and_autoframe(raw_pil, scene_mode=scene_mode)
    sharpness_after = _calc_sharpness_pct(enhanced_pil)

    codes = _decode_qr_and_barcodes(enhanced_pil)
    if not codes:
        codes = _decode_qr_and_barcodes(raw_pil)

    ocr_text = manual_hint_text or ""
    if HAS_TESSERACT:
        try:
            ocr_text = (pytesseract.image_to_string(enhanced_pil, lang="rus+eng") + "\n" + ocr_text).strip()
        except Exception:
            pass

    combined_text = f"{ocr_text}\n" + " ".join(c["raw"] for c in codes)
    axes, elevation = _extract_axes_and_elevation(combined_text)
    low = combined_text.lower()

    if any(w in low for w in ("универсальный передаточный", "упд", "накладная", "торг-12", "грузоотправитель")) or any(c["parsed"].get("inn") for c in codes):
        doc_kind = "UPD_INVOICE"
        doc_kind_label = "🧾 Накладная / УПД (Приход в Склад и 1С)"
    elif any(w in low for w in ("паспорт качества", "сертификат", "гост", "фз-123", "партия", "соответствия")):
        doc_kind = "QUALITY_CERT"
        doc_kind_label = "📜 Паспорт качества / Сертификат (в ИД и АОСР)"
    elif codes or any(w in low for w in ("барабан", "масса брутто", "этикетка", "артикул")):
        doc_kind = "TAG_LABEL"
        doc_kind_label = "🏷️ Бирка / Этикетка партии / Барабан"
    else:
        doc_kind = "FIELD_NODE"
        doc_kind_label = "📐 Фото узла / Осей со стройплощадки"

    matched_rd = []
    words = [w for w in re.findall(r'[а-яёa-z0-9\-]{4,}', low) if not w.isdigit()][:12]
    if words:
        q_filter = PurchaseRequest.objects.none()
        for w in words[:5]:
            q_filter = q_filter | PurchaseRequest.objects.filter(material_name__icontains=w)
        seen = set()
        for req in q_filter[:15]:
            if req.material_name not in seen:
                seen.add(req.material_name)
                matched_rd.append({
                    "material_name": req.material_name,
                    "required_qty": float(req.required_qty),
                    "unit": req.unit,
                    "doc_title": req.document.title if req.document else "РД",
                })

    return {
        "ok": True,
        "scene_info": vision_meta,
        "sharpness_before_pct": sharpness_before,
        "sharpness_after_pct": sharpness_after,
        "quality_warning": "⚠️ Сильное размытие — лучше переснять" if sharpness_after < 18.0 else "✅ Контрастный кадр (готов для OCR/1С)",
        "doc_kind": doc_kind,
        "doc_kind_label": doc_kind_label,
        "codes_found": codes,
        "detected_axes": axes,
        "detected_elevation": elevation,
        "ocr_preview": ocr_text[:600],
        "matched_rd_items": matched_rd[:5],
    }


def split_collage_and_match_positions(image_path: str) -> list[dict]:
    """
    ????????? ?????? ?? ?????????? ????????? ??? ?? ????????? ????? ?? ??????? ????????????
    ? ???????????? ???????????? ??? ? ????????? ????????? PurchaseRequest.
    """
    import os, re
    from PIL import Image, ImageOps
    from storage_control.models import PurchaseRequest

    img = Image.open(image_path).convert("RGB")
    w, h = img.size
    # ???? ?????? ????????? (??????? ??? ?????????? ? ??????????? ???????), ????? ?? ????? 2x2 ??? 3x2
    crops = []
    if w >= 900 and h >= 900:
        cols = 3 if w > h * 1.15 else 2
        rows = 2
        cw, ch = w // cols, h // rows
        for r in range(rows):
            for c in range(cols):
                box = (c * cw, r * ch, min(w, (c + 1) * cw), min(h, (r + 1) * ch))
                crops.append(img.crop(box))
    else:
        crops = [img]

    results = []
    all_reqs = list(PurchaseRequest.objects.values("id", "material_name", "unit"))
    for idx, sub in enumerate(crops, start=1):
        up = ImageOps.autocontrast(sub.resize((sub.width * 2, sub.height * 2)))
        txt = ""
        try:
            import pytesseract
            txt = pytesseract.image_to_string(up, lang="rus+eng")
        except Exception:
            pass
        m_doc = re.search(r'(?:\u0420\u0414\u041a|\u2116)[\-\s]?([A-Z\u0410-\u042f0-9\-]{3,16})', txt)
        m_inn = re.search(r'\b(\d{10}|\d{12})\b', txt)
        matched_req = None
        for rq in all_reqs:
            first_word = (rq["material_name"] or "").split() if (rq["material_name"] or "").split() else ""
            if len(first_word) >= 4 and first_word.lower() in txt.lower():
                matched_req = rq
                break
        results.append({
            "card_index": idx,
            "doc_number": m_doc.group(0) if m_doc else f"\u041b\u0438\u0441\u0442 #{idx}",
            "inn": m_inn.group(1) if m_inn else "",
            "matched_position": matched_req["material_name"] if matched_req else "\u0413\u043e\u0442\u043e\u0432\u043e \u043a \u043f\u0440\u0438\u0432\u044f\u0437\u043a\u0435 \u0432 1\u0421",
            "raw_snippet": re.sub(r'\s+', ' ', txt)[:160],
        })
    return results
