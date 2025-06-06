# translator_api.py
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from core.translator import translate_with_gpt, detect_source_lang

app = FastAPI()
client = None  # 由 run_api_service.py 注入

def init_client(api_key: str):
    global client
    client = OpenAI(api_key=api_key)

class TranslationRequest(BaseModel):
    text: str
    target_language: str

@app.post("/translate")
async def translate(req: TranslationRequest):
    if not client:
        return {"error": "API client not initialized."}
    try:
        detected = detect_source_lang(req.text)
        translated = translate_with_gpt(req.text, req.target_language, client)
        return {"detected": detected, "translated": translated}
    except Exception as e:
        return {"error": str(e)}
