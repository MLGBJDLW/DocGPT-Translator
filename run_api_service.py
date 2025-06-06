from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from openai import OpenAI
from core.translator import translate_with_gpt, detect_source_lang
from translator_helpers_regex import smart_translate
from file_reader import read_docx, read_pdf
import uvicorn
import tempfile

app = FastAPI()

class TranslateRequest(BaseModel):
    text: str
    target_lang: str
    api_key: str

@app.post("/translate_text")
def translate_text(req: TranslateRequest):
    client = OpenAI(api_key=req.api_key)
    detected = detect_source_lang(req.text)
    translated = smart_translate(req.text, req.target_lang, client, translate_with_gpt)
    return {"detected": detected, "translated": translated}

@app.post("/translate_file")
async def translate_file(file: UploadFile = File(...), target_lang: str = "English", api_key: str = ""):
    client = OpenAI(api_key=api_key)
    
    # Save to temp file
    suffix = file.filename.split(".")[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix="." + suffix) as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name

    # Read content
    if file.filename.endswith(".docx"):
        paragraphs = read_docx(tmp_path)
    elif file.filename.endswith(".pdf"):
        paragraphs = read_pdf(tmp_path)
    else:
        return {"error": "Unsupported file format"}

    full_text = "\n".join(paragraphs)
    detected = detect_source_lang(full_text)
    translated = smart_translate(full_text, target_lang, client, translate_with_gpt)
    
    return {"detected": detected, "translated": translated}
    
if __name__ == "__main__":
    uvicorn.run("run_api_service:app", host="127.0.0.1", port=8000)
