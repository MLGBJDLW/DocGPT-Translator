import easyocr
import pyautogui
import torch
import numpy as np
from core.ocr_selector import capture_rectangle
from core.translator import translate_with_gpt, detect_source_lang

# 初始化 EasyOCR（支持 GPU 可改为 gpu=True）
reader = easyocr.Reader(['en', 'ja'], gpu=torch.cuda.is_available())

# 捕捉手动区域，OCR + 翻译
def capture_and_ocr_translate(client):
    bbox = capture_rectangle()
    if not bbox or len(bbox) != 4:
        return "❌ Failed to get region."

    x1, y1, x2, y2 = map(int, bbox)
    region = (x1, y1, x2 - x1, y2 - y1)
    screenshot = pyautogui.screenshot(region=region)
    img_np = np.array(screenshot)

    results = reader.readtext(img_np, detail=0)
    joined_text = "\n".join(results)

    if not joined_text.strip():
        return "❌ No text detected."

    detected = detect_source_lang(joined_text)
    translated = translate_with_gpt(joined_text, "Chinese", client)

    return f"[Detected: {detected}]\n\n{translated}"

# 使用固定区域进行 OCR + 翻译
def capture_and_ocr_translate_fixed(client, region):
    if not region or len(region) != 4:
        return "❌ Invalid fixed region."

    screenshot = pyautogui.screenshot(region=region)
    img_np = np.array(screenshot)

    results = reader.readtext(img_np, detail=0)
    joined_text = "\n".join(results)

    if not joined_text.strip():
        return "❌ No text detected in fixed region."

    detected = detect_source_lang(joined_text)
    translated = translate_with_gpt(joined_text, "Chinese", client)

    return f"[Detected: {detected}]\n\n{translated}"

# 仅识别文本（不翻译），用于比对判断内容变化
def capture_text_only(region):
    x, y, width, height = region
    screenshot = pyautogui.screenshot(region=region)
    img_np = np.array(screenshot)

    results = reader.readtext(img_np, detail=0)
    joined_text = "\n".join(results)
    return joined_text.strip()
