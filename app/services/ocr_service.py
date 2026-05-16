import logging
import os
from typing import Optional

from PIL import Image, ImageEnhance, ImageFilter

logger = logging.getLogger(__name__)

_reader = None


def _get_reader():
    global _reader
    if _reader is None:
        import easyocr
        logger.info("Loading EasyOCR reader (ch_sim + en)...")
        _reader = easyocr.Reader(["ch_sim", "en"], gpu=False)
        logger.info("EasyOCR reader loaded")
    return _reader


def preprocess_image(image_path: str) -> Image.Image:
    img = Image.open(image_path)
    img = img.convert("L")
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.5)
    img = img.filter(ImageFilter.SHARPEN)
    return img


def extract_text_from_image(image_path: str) -> str:
    reader = _get_reader()
    preprocessed = preprocess_image(image_path)
    temp_path = image_path + "_processed.png"
    preprocessed.save(temp_path)

    try:
        result = reader.readtext(temp_path, detail=1, paragraph=True)
        texts = []
        for item in result:
            text = item[1]
            texts.append(text)
        return "\n".join(texts)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def extract_text_with_tesseract(image_path: str) -> Optional[str]:
    try:
        import pytesseract
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang="chi_sim+eng")
        return text.strip() if text.strip() else None
    except Exception as e:
        logger.warning(f"Tesseract OCR failed: {e}")
        return None


def ocr_image(image_path: str) -> str:
    try:
        text = extract_text_from_image(image_path)
        if text.strip():
            return text
    except Exception as e:
        logger.warning(f"EasyOCR failed: {e}, trying Tesseract fallback...")

    fallback = extract_text_with_tesseract(image_path)
    if fallback:
        return fallback

    raise RuntimeError("所有 OCR 方法均失败，请尝试粘贴文本方式输入")
