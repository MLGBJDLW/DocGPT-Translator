# 修复并增强支持模型切换的 main_window.py
# （在你原有的基础上保留 load_file，添加 model 字段处理和传参）
import customtkinter as ctk
from ui.tabs.text_translate_tab import build_text_tab
from ui.ocr.fixed_ocr_tab import build_fixed_ocr_tab
from ui.ocr.floating_ocr_tab import build_floating_ocr_tab
from ui.settings_window import open_settings_window
from ui.tray_icon import create_tray_icon
from core.translator import language_codes, detect_source_lang, translate_with_gpt
from core.ocr_handler import capture_and_ocr_translate
from core.save_history import save_history
from tkinter import filedialog, messagebox
from file_reader import read_docx, read_pdf
import json
import os
import threading
import keyboard
import pyautogui
import pyperclip
from openai import OpenAI

SETTINGS_FILE = os.path.expanduser("~/.gpt_translator_settings.json")

class TranslatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("GPT Translator")
        self.geometry("600x620")

        self.api_key = None
        self.client = None
        self.hotkey = "ctrl+shift+t"
        self.theme = "System"
        self.auto_detect = True
        self.model = "gpt-3.5-turbo"
        self.last_used_language = "English"
        self.load_settings()
        ctk.set_appearance_mode(self.theme)
        ctk.set_default_color_theme("blue")

        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_text = self.tabs.add("✍️ Text Translate")
        build_text_tab(self)

        self.tab_fixed = self.tabs.add("📌 Fixed OCR")
        build_fixed_ocr_tab(self)

        self.tab_float = self.tabs.add("🧊 Floating OCR")
        build_floating_ocr_tab(self)

        self.settings_button = ctk.CTkButton(self, text="⚙️ Settings", command=lambda: open_settings_window(self))
        self.settings_button.pack(pady=(0, 10), fill="x", padx=40)

        threading.Thread(target=self.register_hotkey_listener, daemon=True).start()
        self.protocol("WM_DELETE_WINDOW", self.hide_to_tray)
        create_tray_icon(self)

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.api_key = data.get("api_key", None)
                    self.hotkey = data.get("hotkey", "ctrl+shift+t")
                    self.theme = data.get("theme", "System")
                    self.auto_detect = data.get("auto_detect", True)
                    self.last_used_language = data.get("last_used_language", "English")
                    self.model = data.get("model", "gpt-3.5-turbo")
            except Exception:
                self.api_key = None

    def save_settings(self, key, hotkey, theme, auto_detect, last_used_language, model):
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "api_key": key,
                    "hotkey": hotkey,
                    "theme": theme,
                    "auto_detect": auto_detect,
                    "last_used_language": last_used_language,
                    "model": model
                }, f)
        except Exception:
            pass

    def hide_to_tray(self):
        self.withdraw()

    def register_hotkey_listener(self):
        try:
            keyboard.add_hotkey(self.hotkey, self.hotkey_translate)
            keyboard.wait()
        except:
            pass

    def translate_text(self):
        if not self.api_key:
            self.text_output.delete("0.0", "end")
            self.text_output.insert("0.0", "❌ Please set your OpenAI API Key in Settings.")
            return
        self.client = OpenAI(api_key=self.api_key)
        raw_text = self.text_input.get("0.0", "end").strip()
        if not raw_text:
            self.text_output.delete("0.0", "end")
            self.text_output.insert("0.0", "❌ No text provided.")
            return
        detected_lang = detect_source_lang(raw_text)
        self.label_detected.configure(text=f"Detected Language: {detected_lang}")
        target_lang = self.combo_lang.get()
        self.text_output.delete("0.0", "end")
        self.text_output.insert("0.0", "🔄 Translating, please wait...")
        self.update_idletasks()
        try:
            translated = translate_with_gpt(raw_text, target_lang, self.client, model=self.model)
            self.text_output.delete("0.0", "end")
            self.text_output.insert("0.0", translated)
            save_history({"source": raw_text, "translated": translated, "target_language": target_lang})
        except Exception as e:
            self.text_output.delete("0.0", "end")
            self.text_output.insert("0.0", f"❌ Translation failed:\n{str(e)}")

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[('Document', "*.docx *.pdf")])
        if not path:
            return
        try:
            if path.endswith(".docx"):
                content = read_docx(path)
            elif path.endswith(".pdf"):
                content = read_pdf(path)
            else:
                messagebox.showerror("Unsupported Format", "Only .docx and .pdf files are supported.")
                return
            self.text_input.delete("0.0", "end")
            self.text_input.insert("0.0", "\n".join(content))
        except Exception as e:
            messagebox.showerror("File Read Error", f"Failed to read file:\n{str(e)}")

    def run_ocr_translate(self):
        if not self.api_key:
            messagebox.showerror("Missing API Key", "Please set your OpenAI API Key in Settings.")
            return
        if not self.client:
            self.client = OpenAI(api_key=self.api_key)
        try:
            result = capture_and_ocr_translate(self.client)
            self.text_output.delete("0.0", "end")
            self.text_output.insert("0.0", result)
        except Exception as e:
            self.text_output.delete("0.0", "end")
            self.text_output.insert("0.0", f"❌ OCR Translation failed:\n{str(e)}")

    def hotkey_translate(self):
        if not self.api_key:
            return
        self.client = OpenAI(api_key=self.api_key)
        pyautogui.hotkey("ctrl", "c")
        import time
        time.sleep(0.3)
        text = pyperclip.paste().strip()
        if not text:
            return
        detected_lang = detect_source_lang(text)
        self.label_detected.configure(text=f"Detected Language: {detected_lang}")
        target_lang = self.combo_lang.get()
        try:
            translated = translate_with_gpt(text, target_lang, self.client, model=self.model)
            self.text_output.delete("0.0", "end")
            self.text_output.insert("0.0", translated)
        except Exception as e:
            self.text_output.delete("0.0", "end")
            self.text_output.insert("0.0", f"❌ Translation failed:\n{str(e)}")
