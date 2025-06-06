
# GPT Translator with GUI, OCR, Tray, File Import, Logging, History
import customtkinter as ctk
import pyperclip
from openai import OpenAI
import os
import json
import keyboard
import threading
from tkinter import messagebox, filedialog
from core.translator import translate_with_gpt, detect_source_lang, language_codes
from core.ocr_handler import capture_and_ocr_translate
from file_reader import read_docx, read_pdf
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw
import time

SETTINGS_FILE = os.path.expanduser("~/.gpt_translator_settings.json")
HISTORY_FILE = os.path.expanduser("~/.gpt_translator_history.json")
LOG_FILE = os.path.expanduser("~/translator.log")

def apply_theme(mode):
    ctk.set_appearance_mode(mode)
    ctk.set_default_color_theme("blue")

def log_error(error_msg):
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(error_msg + "\n")

def save_history(entry):
    try:
        history = []
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        history.insert(0, entry)
        history = history[:10]
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception as e:
        log_error("[History Save Error] " + str(e))

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
        self.last_used_language = "English"
        self.load_settings()
        apply_theme(self.theme)

        self.label_lang = ctk.CTkLabel(self, text="Target Language:")
        self.label_lang.pack(pady=(10, 5))

        self.combo_lang = ctk.CTkComboBox(self, values=list(language_codes.keys()), width=200)
        self.combo_lang.pack(pady=(0, 10))
        self.combo_lang.set(self.last_used_language)

        self.text_input = ctk.CTkTextbox(self, height=120)
        self.text_input.pack(padx=20, pady=(5, 10), fill="both")
        self.text_input.insert("0.0", "Paste or type text to translate...")

        self.label_detected = ctk.CTkLabel(self, text="Detected Language: Unknown")
        self.label_detected.pack(pady=(5, 5))

        self.button_translate = ctk.CTkButton(self, text="Translate", command=self.translate_text)
        self.button_translate.pack(pady=10, fill="x", padx=40)

        self.text_output = ctk.CTkTextbox(self, height=200)
        self.text_output.pack(padx=20, pady=(5, 10), fill="both")

        self.settings_button = ctk.CTkButton(self, text="⚙️ Settings", command=self.open_settings_window)
        self.settings_button.pack(pady=(5, 5), fill="x", padx=40)

        self.load_file_button = ctk.CTkButton(self, text="📂 Load .docx or .pdf", command=self.load_file)
        self.load_file_button.pack(pady=(0, 5), fill="x", padx=40)

        self.ocr_button = ctk.CTkButton(self, text="🖼 OCR Screenshot", command=self.run_ocr_translate)
        self.ocr_button.pack(pady=(0, 10), fill="x", padx=40)

        threading.Thread(target=self.register_hotkey_listener, daemon=True).start()

        if self.auto_detect:
            self.combo_lang.configure(state="disabled")

        self.protocol("WM_DELETE_WINDOW", self.hide_to_tray)
        self.create_tray_icon()

    def create_tray_icon(self):
        img = Image.new('RGB', (64, 64), color=(40, 40, 40))
        draw = ImageDraw.Draw(img)
        draw.text((20, 20), "T", fill=(255, 255, 255))

        def on_show(): self.deiconify()
        def on_quit(icon, item): icon.stop(); self.quit()

        menu = Menu(MenuItem('Show Translator', on_show), MenuItem('Quit', on_quit))
        icon = Icon("GPT Translator", img, "GPT Translator", menu)
        self.tray_icon = icon
        threading.Thread(target=icon.run, daemon=True).start()

    def hide_to_tray(self): self.withdraw()

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("Document", "*.docx *.pdf")])
        if not path:
            return
        try:
            if path.endswith(".docx"):
                content = read_docx(path)
            elif path.endswith(".pdf"):
                content = read_pdf(path)
            else:
                messagebox.showerror("Unsupported", "Please select a .docx or .pdf file.")
                return
            self.text_input.delete("0.0", "end")
            self.text_input.insert("0.0", "\n".join(content))
        except Exception as e:
            messagebox.showerror("File Load Error", str(e))
            log_error("[File Load Error] " + str(e))

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
        target_lang = self.combo_lang.get() if not self.auto_detect else "English"
        self.text_output.delete("0.0", "end")
        self.text_output.insert("0.0", "🔄 Translating, please wait...")
        self.update_idletasks()
        try:
            translated = translate_with_gpt(raw_text, target_lang, self.client)
            self.text_output.delete("0.0", "end")
            self.text_output.insert("0.0", translated)
            save_history({"source": raw_text, "translated": translated, "target_language": target_lang})
        except Exception as e:
            self.text_output.delete("0.0", "end")
            self.text_output.insert("0.0", f"❌ Translation failed:\n{str(e)}")
            log_error("[Translate Error] " + str(e))

    def open_settings_window(self):
        settings = ctk.CTkToplevel(self)
        settings.title("Settings")
        settings.geometry("400x300")

        ctk.CTkLabel(settings, text="OpenAI API Key:").pack(pady=(15, 5))
        entry_key = ctk.CTkEntry(settings, show="*")
        entry_key.pack(pady=(0, 10), fill="x", padx=20)
        if self.api_key: entry_key.insert(0, self.api_key)

        ctk.CTkLabel(settings, text="Translation Hotkey:").pack(pady=(10, 5))
        entry_hotkey = ctk.CTkEntry(settings)
        entry_hotkey.pack(pady=(0, 10), fill="x", padx=20)
        entry_hotkey.insert(0, self.hotkey)

        ctk.CTkLabel(settings, text="Theme:").pack(pady=(10, 5))
        combo_theme = ctk.CTkComboBox(settings, values=["System", "Light", "Dark"])
        combo_theme.pack(pady=(0, 10), fill="x", padx=20)
        combo_theme.set(self.theme)

        frame_auto = ctk.CTkFrame(settings, fg_color="transparent")
        frame_auto.pack(pady=(10, 10), fill="x", padx=20)
        label_auto = ctk.CTkLabel(frame_auto, text="🔍 Auto-detect Source Language:")
        label_auto.pack(side="left")
        auto_var = ctk.BooleanVar(value=self.auto_detect)

        def toggle_language_state():
            self.combo_lang.configure(state="disabled" if auto_var.get() else "normal")

        check_auto = ctk.CTkCheckBox(frame_auto, text="", variable=auto_var, command=toggle_language_state)
        check_auto.pack(side="left", padx=(10, 0))

        def save_key():
            self.api_key = entry_key.get().strip()
            self.hotkey = entry_hotkey.get().strip()
            self.theme = combo_theme.get()
            self.auto_detect = auto_var.get()
            self.last_used_language = self.combo_lang.get()
            self.save_settings(self.api_key, self.hotkey, self.theme, self.auto_detect, self.last_used_language)
            apply_theme(self.theme)
            settings.destroy()
            keyboard.clear_all_hotkeys()
            keyboard.add_hotkey(self.hotkey, self.hotkey_translate)
            toggle_language_state()

        ctk.CTkButton(settings, text="Save", command=save_key).pack(pady=(5, 10), fill="x", padx=100)

    def hotkey_translate(self):
        if not self.api_key:
            return
        self.client = OpenAI(api_key=self.api_key)
        import pyautogui
        pyautogui.hotkey("ctrl", "c")
        time.sleep(0.3)
        text = pyperclip.paste().strip()
        if not text:
            return
        detected_lang = detect_source_lang(text)
        self.label_detected.configure(text=f"Detected Language: {detected_lang}")
        target_lang = self.combo_lang.get() if not self.auto_detect else "English"
        try:
            translated = translate_with_gpt(text, target_lang, self.client)
            self.text_output.delete("0.0", "end")
            self.text_output.insert("0.0", translated)
        except Exception as e:
            self.text_output.delete("0.0", "end")
            self.text_output.insert("0.0", f"❌ Translation failed:\n{str(e)}")
            
    def run_ocr_translate(self):
        if not self.api_key:
            messagebox.showerror("Missing API Key", "Please set your OpenAI API Key in Settings.")
            return

        if not self.client:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)

        try:
            result = capture_and_ocr_translate(self.client)
            self.text_output.delete("0.0", "end")
            self.text_output.insert("0.0", result)
        except Exception as e:
            self.text_output.delete("0.0", "end")
            self.text_output.insert("0.0", f"❌ OCR Translation failed:\n{str(e)}")

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
            except Exception:
                self.api_key = None

    def save_settings(self, key, hotkey, theme, auto_detect, last_used_language):
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "api_key": key,
                    "hotkey": hotkey,
                    "theme": theme,
                    "auto_detect": auto_detect,
                    "last_used_language": last_used_language
                }, f)
        except Exception:
            pass

    def register_hotkey_listener(self):
        try:
            keyboard.add_hotkey(self.hotkey, self.hotkey_translate)
            keyboard.wait()
        except:
            pass

if __name__ == "__main__":
    app = TranslatorApp()
    app.mainloop()
