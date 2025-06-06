import customtkinter as ctk
import os
import json

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