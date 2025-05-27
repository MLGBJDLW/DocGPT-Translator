import os
import json
import customtkinter as ctk
import threading
import pyperclip
from openai import OpenAI
from tkinter import filedialog, messagebox

from translator import translate_with_gpt, detect_source_lang, language_codes
from file_reader import read_docx, read_pdf
from ui.settings_ui import open_settings_window
from ui.tray_icon import create_tray_icon
from ui.utils import apply_theme, save_history, log_error
from ui.history_viewer import show_history_popup
from translator_helpers_regex import smart_translate


SETTINGS_FILE = os.path.expanduser("~/.gpt_translator_settings.json")

class TranslatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("GPT Translator")
        self.geometry("600x620")

        # Load settings
        self.api_key = None
        self.client = None
        self.hotkey = "ctrl+shift+t"
        self.theme = "System"
        self.auto_detect = True
        self.last_used_language = "English"
        self.minimize_on_close = True
        self.load_settings()
        apply_theme(self.theme)

        # UI Components
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

        self.settings_button = ctk.CTkButton(self, text="⚙️ Settings", command=lambda: open_settings_window(self))
        self.settings_button.pack(pady=(5, 5), fill="x", padx=40)
        
        self.history_button = ctk.CTkButton(self, text="📜 View History", command=lambda: show_history_popup(self))
        self.history_button.pack(pady=(0, 5), fill="x", padx=40)

        self.load_file_button = ctk.CTkButton(self, text="📂 Load .docx or .pdf", command=self.load_file)
        self.load_file_button.pack(pady=(0, 10), fill="x", padx=40)

        threading.Thread(target=self.register_hotkey_listener, daemon=True).start()

        if self.auto_detect:
            self.combo_lang.configure(state="disabled")

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        create_tray_icon(self)

    def on_close(self):
        if self.minimize_on_close:
            self.withdraw()
        else:
            self.destroy()
    
    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    data = json.load(f)
                    self.api_key = data.get("api_key", None)
                    self.hotkey = data.get("hotkey", "ctrl+shift+t")
                    self.theme = data.get("theme", "System")
                    self.auto_detect = data.get("auto_detect", True)
                    self.last_used_language = data.get("last_used_language", "English")
                    self.minimize_on_close = data.get("minimize_on_close", True)
            except Exception:
                self.api_key = None
                self.last_used_language = "English"
                self.minimize_on_close = True
        else:
            self.last_used_language = "English"
            self.minimize_on_close = True
            
    def save_settings(self, key, hotkey, theme, auto_detect, last_used_language, minimize_on_close):
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump({
                    "api_key": key,
                    "hotkey": hotkey,
                    "theme": theme,
                    "auto_detect": auto_detect,
                    "last_used_language": last_used_language,
                    "minimize_on_close": minimize_on_close
                }, f)
        except Exception:
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
        target_lang = self.combo_lang.get() if not self.auto_detect else "English"

        self.text_output.delete("0.0", "end")
        self.text_output.insert("0.0", "🔄 Translating, please wait...")
        self.update_idletasks()

        try:
            result = smart_translate(raw_text, target_lang, self.client, translate_with_gpt)
            pyperclip.copy(result)
            self.text_output.delete("0.0", "end")
            self.text_output.insert("0.0", result + "\n\n📋 Copied to clipboard!")
            save_history({
                "source": raw_text,
                "translated": result,
                "target_language": target_lang
            })
        except Exception as e:
            self.text_output.delete("0.0", "end")
            self.text_output.insert("0.0", f"❌ Translation failed:\n{str(e)}")
            log_error("[Translate Error] " + str(e))


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

    def hotkey_translate(self):
        if not self.api_key:
            return
        self.client = OpenAI(api_key=self.api_key)
        import pyautogui, time
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
            pyperclip.copy(translated)
            self.text_output.delete("0.0", "end")
            self.text_output.insert("0.0", translated + "\n\n📋 Copied to clipboard!")
        except Exception as e:
            self.text_output.delete("0.0", "end")
            self.text_output.insert("0.0", f"❌ Translation failed:\n{str(e)}")

    def register_hotkey_listener(self):
        try:
            import keyboard
            keyboard.add_hotkey(self.hotkey, self.hotkey_translate)
            keyboard.wait()
        except:
            pass