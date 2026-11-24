# -*- coding: utf-8 -*-
import logging
import numpy as np
import cv2

logger = logging.getLogger(__name__)
_OCR_ENGINE = None


def _get_ocr():
    global _OCR_ENGINE
    if _OCR_ENGINE is None:
        try:
            from rapidocr_onnxruntime import RapidOCR
            _OCR_ENGINE = RapidOCR()
        except Exception as exc:
            logger.error("Ошибка загрузки RapidOCR: %s", exc)
            _OCR_ENGINE = False
    return _OCR_ENGINE if _OCR_ENGINE is not False else None


def _preprocess_scan(png_bytes: bytes) -> np.ndarray:
    """Предобработка скана: перевод в оттенки серого и повышение контраста (CLAHE)."""
    arr = np.frombuffer(png_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_GRAYSCALE)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(img)


def read_vector_or_raster(page) -> dict:
    """Переключатель: если чертёж векторный — берёт 100% точный текст; если скан — улучшает и запускает OCR."""
    drawings_count = len(page.get_drawings())
    vector_text = page.get_text("text").strip()

    if len(vector_text) >= 15:
        return {
            "mode": f"ВЕКТОР (линий: {drawings_count})",
            "text": vector_text,
            "is_vector": True,
        }

    engine = _get_ocr()
    if not engine:
        return {"mode": "СКАН (OCR недоступен)", "text": "", "is_vector": False}

    png_bytes = page.get_pixmap(dpi=200).tobytes("png")
    enhanced_img = _preprocess_scan(png_bytes)
    result, _ = engine(enhanced_img)
    ocr_text = "\n".join(item[1] for item in (result or []) if len(item) > 1 and item[1])

    return {
        "mode": "РАСТР / OCR (Контраст+)",
        "text": ocr_text.strip(),
        "is_vector": False,
    }
