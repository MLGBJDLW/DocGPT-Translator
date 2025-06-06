import easyocr
import pyautogui
import numpy as np
from core.ocr_selector import capture_rectangle
from core.translator import translate_with_gpt, detect_source_lang

reader = easyocr.Reader(['en', 'ja'], gpu=False)

# Capture a region of the screen, perform OCR, and translate the text
def capture_and_ocr_translate(client):
    bbox = capture_rectangle()
    if not bbox or len(bbox) != 4:
        return "❌ Failed to get region."

    x1, y1, x2, y2 = map(int, bbox)
    region = (x1, y1, x2 - x1, y2 - y1)
    screenshot = pyautogui.screenshot(region=region)
    img_np = np.array(screenshot)

    results = reader.readtext(img_np)
    texts = [text[1] for text in results]
    joined_text = "\n".join(texts)

    if not joined_text.strip():
        return "❌ No text detected."

    detected = detect_source_lang(joined_text)
    translated = translate_with_gpt(joined_text, "Chinese", client)

    return f"[Detected: {detected}]\n\n{translated}"

# Capture and OCR + Translate with fixed region
def capture_and_ocr_translate_fixed(client, region):
    """
    使用给定区域进行 OCR + 翻译
    region: (x, y, width, height)
    """
    if not region or len(region) != 4:
        return "❌ Invalid fixed region."

    screenshot = pyautogui.screenshot(region=region)
    img_np = np.array(screenshot)

    results = reader.readtext(img_np)
    texts = [text[1] for text in results]
    joined_text = "\n".join(texts)

    if not joined_text.strip():
        return "❌ No text detected in fixed region."

    detected = detect_source_lang(joined_text)
    translated = translate_with_gpt(joined_text, "Chinese", client)

    return f"[Detected: {detected}]\n\n{translated}"

