from langdetect import detect
from openai import OpenAI
from openai.types.chat import ChatCompletion

# Supported human-readable languages
language_codes = {
    "English": "English",
    "Spanish": "Spanish",
    "French": "French",
    "German": "German",
    "Chinese": "Chinese",
    "Japanese": "Japanese",
    "Korean": "Korean",
    "Russian": "Russian",
    "Arabic": "Arabic",
}

def detect_source_lang(text: str) -> str:
    try:
        code = detect(text)
        fallback = {
            "en": "English",
            "zh-cn": "Chinese",
            "zh-tw": "Chinese",
            "fr": "French",
            "de": "German",
            "es": "Spanish",
            "ja": "Japanese",
            "ko": "Korean",
            "ru": "Russian",
            "ar": "Arabic"
        }
        return fallback.get(code, "English")
    except Exception:
        return "English"

def translate_with_gpt(text: str, target_language: str, client: OpenAI) -> str:
    if not hasattr(client, "chat") or not hasattr(client.chat, "completions"):
        raise ValueError("Provided client is not a valid OpenAI client. Make sure you passed OpenAI(api_key=...)")

    prompt = f"Translate the following text into {target_language}:\n\n{text}"

    try:
        response: ChatCompletion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful translation assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Translation failed: {str(e)}"
