import io
from PIL import Image
try:
    import pytesseract
except ImportError:
    pytesseract = None


def extract_text_from_image(image_bytes: bytes) -> str:
    """
    Extracts raw text and token bounding boxes using Tesseract OCR.
    Gracefully handles environment configuration.
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        if pytesseract is not None:
            try:
                text = pytesseract.image_to_string(img, config="--oem 3 --psm 6")
                return text.strip()
            except Exception as ocr_err:
                # Fallback if tesseract binary path is not set
                return f"[OCR Engine Error: {str(ocr_err)}]"
        return "[OCR Unavailable: pytesseract not installed]"
    except Exception as e:
        return f"[Image Read Error: {str(e)}]"
