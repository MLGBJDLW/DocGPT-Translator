# DocGPT Translator

**DocGPT Translator** is a small experimental desktop app that uses OpenAI GPT models to translate text and perform OCR on selected screen regions. It is designed for casual usage such as reading, basic document assistance, or game translation.

---

## Features

- 📝 Text translation with auto language detection
- 📷 OCR translation by selecting screen regions
- 📂 Load `.docx` and `.pdf` documents for translation
- 🕹️ Hotkey trigger (default `Ctrl+Shift+T`) to translate copied text
- 💾 Saves translation history locally (latest 10 entries)
- 🧪 API Key is configurable via a settings menu
- 🖼 GUI built with `customtkinter`, supports dark/light/system themes

---

## Installation

```bash
git clone https://github.com/MLGBJDLW/DocGPT-Translator.git
cd DocGPT-Translator
pip install -r requirements.txt
python main.py
```

---

## Notes

- The app uses the OpenAI Python SDK (`openai>=1.x`)
- OCR is handled by `easyocr`, which supports multiple languages
- This is a **work-in-progress** prototype intended for testing and personal use
- GPU is recommended for faster OCR, but not required

---

## Folder Structure

```
.
├── main.py
├── requirements.txt
├── core/
│   ├── ocr_handler.py
│   ├── ocr_selector.py
│   └── translator.py
├── ui/
│   ├── translator_gui.py
│   ├── settings_ui.py
│   └── tray_icon.py
└── README.md
```

---

## License

MIT License  
© 2024 [MLGBJDLW](https://github.com/MLGBJDLW)