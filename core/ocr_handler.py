import easyocr
import pyautogui
import torch
import numpy as np
from core.ocr_selector import capture_rectangle
from core.translator import translate_with_gpt, detect_source_lang

# Default language for OCR
DEFAULT_LANGS = ['ch_sim', 'en']

def get_easyocr_reader(langs=None):
    langs = langs or DEFAULT_LANGS
    if any(l in langs for l in ['ch_sim', 'ch_tra', 'ja', 'ko']):
        return easyocr.Reader(['en'] + [l for l in langs if l in ['ch_sim', 'ch_tra', 'ja', 'ko']], gpu=torch.cuda.is_available())
    else:
        return easyocr.Reader(langs, gpu=torch.cuda.is_available())
    
# 公共处理函数：OCR + 拼接
def process_ocr(img_np, langs=None):
    reader = get_easyocr_reader(langs)
    results = reader.readtext(img_np, detail=0)

    if isinstance(results[0], str):
        joined_text = "\n".join(results)
    else:
        joined_text = "\n".join([text for _, text, _ in results])

    return joined_text.strip()

# 捕捉手动区域，OCR + 翻译
def capture_and_ocr_translate(client, langs=None):
    bbox = capture_rectangle()
    if not bbox or len(bbox) != 4:
        return "❌ Failed to get region."

    x1, y1, x2, y2 = map(int, bbox)
    region = (x1, y1, x2 - x1, y2 - y1)
    screenshot = pyautogui.screenshot(region=region)
    img_np = np.array(screenshot)

    joined_text = process_ocr(img_np, langs)

    if not joined_text:
        return "❌ No text detected."

    detected = detect_source_lang(joined_text)
    translated = translate_with_gpt(joined_text, "Chinese", client)

    return f"[Detected: {detected}]\n\n{translated}"

# 使用固定区域进行 OCR + 翻译
def capture_and_ocr_translate_fixed(client, region, langs=None):
    if not region or len(region) != 4:
        return "❌ Invalid fixed region."

    screenshot = pyautogui.screenshot(region=region)
    img_np = np.array(screenshot)

    joined_text = process_ocr(img_np, langs)

    if not joined_text:
        return "❌ No text detected in fixed region."

    detected = detect_source_lang(joined_text)
    translated = translate_with_gpt(joined_text, "Chinese", client)

    return f"[Detected: {detected}]\n\n{translated}"

# 仅识别文本（不翻译），用于比对判断内容变化
def capture_text_only(region, langs=None):
    screenshot = pyautogui.screenshot(region=region)
    img_np = np.array(screenshot)
    return process_ocr(img_np, langs)
