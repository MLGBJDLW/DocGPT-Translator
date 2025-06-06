import customtkinter as ctk
import os
import json
from tkinter import messagebox
import pytesseract

LOG_FILE = os.path.expanduser("~/translator.log")
HISTORY_FILE = os.path.expanduser("~/.gpt_translator_history.json")

def apply_theme(mode):
    ctk.set_appearance_mode(mode)
    ctk.set_default_color_theme("blue")

def log_error(error_msg):
    try:
        with open(LOG_FILE, "a") as log:
            log.write(error_msg + "\n")
    except Exception:
        pass

def save_history(entry):
    try:
        history = []
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
        history.insert(0, entry)
        history = history[:10]  # Keep only the last 10 entries
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        log_error("[History Save Error] " + str(e))
        
def ensure_tesseract_ready():
    # 如果系统未配置 PATH，可手动设置默认安装路径
    default_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.exists(default_path):
        pytesseract.pytesseract.tesseract_cmd = default_path

    try:
        # 尝试运行 tesseract 命令确认安装
        version = pytesseract.get_tesseract_version()
        return True  # ✅ 已安装
    except (EnvironmentError, pytesseract.TesseractNotFoundError):
        # ❌ 未安装，弹窗提醒
        messagebox.showerror(
            "Tesseract Missing",
            "Tesseract-OCR 未安装或未配置到 PATH。\n\n请访问以下地址下载安装：\nhttps://github.com/UB-Mannheim/tesseract/wiki"
        )
        return False