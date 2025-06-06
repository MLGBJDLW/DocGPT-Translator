import tkinter as tk
import time
import threading
from openai import OpenAI
from core.ocr_handler import capture_and_ocr_translate_fixed
import customtkinter as ctk
from tkinter import messagebox

def build_floating_ocr_tab(app):
    app.float_ocr_btn = ctk.CTkButton(app.tab_float, text="🧊 Launch Floating Translate Box", command=lambda: launch_floating_ocr(app))
    app.float_ocr_btn.pack(pady=(20, 10), fill="x", padx=40)

def launch_floating_ocr(app):
    if not app.api_key:
        messagebox.showerror("Missing API Key", "Please set your OpenAI API Key in Settings.")
        return
    app.client = OpenAI(api_key=app.api_key)

    app.float_win = tk.Toplevel(app)
    app.float_win.title("Floating OCR")
    app.float_win.geometry("400x200+300+300")
    app.float_win.overrideredirect(True)
    app.float_win.attributes("-topmost", True)
    app.float_win.configure(bg="#222222")

    app.float_dragging = False
    app.float_paused = False
    app.float_ocr_active = True

    # Create a transparent background for the floating window
    container = tk.Frame(app.float_win, bg="#222222")
    container.pack(expand=True, fill="both")

    app.float_text = tk.Text(container, wrap="word", font=("Arial", 10),
                              bg="#222222", fg="#00FF99", insertbackground="#00FF99", relief="flat")
    app.float_text.pack(expand=True, fill="both", padx=10, pady=(10, 5))
    app.float_text.focus_set()  # Set focus to the text widget

    close_button = tk.Button(
        container,
        text="❌ Close",
        command=lambda: close_floating_ocr(app),
        bg="#444444",
        fg="white"
    )
    close_button.pack(side="bottom", pady=5)

    app.float_text.bind("<Escape>", lambda e: close_floating_ocr(app))
    app.float_win.bind("<Escape>", lambda e: close_floating_ocr(app))

    app.float_win.bind("<ButtonPress-1>", lambda e: start_drag(app, e))
    app.float_win.bind("<B1-Motion>", lambda e: do_drag(app, e))
    app.float_win.bind("<ButtonRelease-1>", lambda e: end_drag(app, e))

    threading.Thread(target=lambda: run_floating_ocr_loop(app), daemon=True).start()

def start_drag(app, event):
    app.float_dragging = True
    app.float_paused = True
    app.drag_start_x = event.x
    app.drag_start_y = event.y

def do_drag(app, event):
    x = app.float_win.winfo_x() + event.x - app.drag_start_x
    y = app.float_win.winfo_y() + event.y - app.drag_start_y
    app.float_win.geometry(f"+{x}+{y}")

def end_drag(app, event):
    app.float_dragging = False
    app.float_paused = False

def run_floating_ocr_loop(app):
    while getattr(app, "float_ocr_active", False):
        if not getattr(app, "float_paused", False):
            try:
                x = app.float_win.winfo_rootx()
                y = app.float_win.winfo_rooty()
                w = app.float_win.winfo_width()
                h = app.float_win.winfo_height()
                region = (x, y, w, h)
                result = capture_and_ocr_translate_fixed(app.client, region)
                app.float_text.delete("1.0", "end")
                app.float_text.insert("1.0", result)
            except Exception as e:
                app.float_text.delete("1.0", "end")
                app.float_text.insert("1.0", f"❌ Error:\n{e}")
        time.sleep(3)

def close_floating_ocr(app):
    app.float_ocr_active = False
    if hasattr(app, "float_win"):
        app.float_win.destroy()
