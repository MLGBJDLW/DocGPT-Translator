import os
import json
from tkinter import Toplevel, Text, END, messagebox

HISTORY_FILE = os.path.expanduser("~/.gpt_translator_history.json")

def show_history_popup(master):
    if not os.path.exists(HISTORY_FILE):
        messagebox.showinfo("No History", "No translation history found.")
        return

    try:
        with open(HISTORY_FILE, "r") as f:
            entries = json.load(f)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load history: {str(e)}")
        return

    popup = Toplevel(master)
    popup.title("Translation History")
    popup.geometry("600x400")

    text = Text(popup, wrap="word")
    text.pack(expand=True, fill="both")

    for item in entries:
        text.insert(END, f"📝 Source:\n{item['source']}\n\n✅ Translated ({item['target_language']}):\n{item['translated']}\n\n{'-'*60}\n\n")

    text.config(state="disabled")