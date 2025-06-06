from core.translator import translate_with_gpt, detect_source_lang, language_codes
from core.ocr_handler import capture_and_ocr_translate
from file_reader import read_docx, read_pdf
from tkinter import messagebox, filedialog
from openai import OpenAI
import customtkinter as ctk

def build_text_tab(app):
    app.label_lang = ctk.CTkLabel(app.tab_text, text="Target Language:")
    app.label_lang.pack(pady=(10, 5))

    app.combo_lang = ctk.CTkComboBox(app.tab_text, values=list(language_codes.keys()), width=200)
    app.combo_lang.pack(pady=(0, 10))
    app.combo_lang.set(app.last_used_language)

    app.text_input = ctk.CTkTextbox(app.tab_text, height=120)
    app.text_input.pack(padx=20, pady=(5, 10), fill="both")
    app.text_input.insert("0.0", "Paste or type text to translate...")

    app.label_detected = ctk.CTkLabel(app.tab_text, text="Detected Language: Unknown")
    app.label_detected.pack(pady=(5, 5))

    app.button_translate = ctk.CTkButton(app.tab_text, text="Translate", command=app.translate_text)
    app.button_translate.pack(pady=10, fill="x", padx=40)

    app.text_output = ctk.CTkTextbox(app.tab_text, height=200)
    app.text_output.pack(padx=20, pady=(5, 10), fill="both")

    app.load_file_button = ctk.CTkButton(app.tab_text, text="📂 Load .docx or .pdf", command=app.load_file)
    app.load_file_button.pack(pady=(0, 5), fill="x", padx=40)

    app.ocr_button = ctk.CTkButton(app.tab_text, text="🖼 OCR Screenshot", command=app.run_ocr_translate)
    app.ocr_button.pack(pady=(0, 10), fill="x", padx=40)
