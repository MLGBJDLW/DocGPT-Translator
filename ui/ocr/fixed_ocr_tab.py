import customtkinter as ctk
from tkinter import messagebox
import threading
import time
from core.ocr_selector import capture_rectangle
from core.ocr_handler import capture_and_ocr_translate_fixed
from openai import OpenAI

def build_fixed_ocr_tab(app):
    app.fixed_region = None
    app.ocr_looping = False

    app.select_region_btn = ctk.CTkButton(app.tab_fixed, text="📌 Select Fixed Region", command=lambda: select_fixed_region(app))
    app.select_region_btn.pack(pady=(10, 5), fill="x", padx=40)

    app.loop_ocr_btn = ctk.CTkButton(app.tab_fixed, text="🔁 Start OCR Loop", command=lambda: start_ocr_loop(app))
    app.loop_ocr_btn.pack(pady=(0, 5), fill="x", padx=40)

    app.stop_loop_btn = ctk.CTkButton(app.tab_fixed, text="⏹ Stop Loop", command=lambda: stop_ocr_loop(app))
    app.stop_loop_btn.pack(pady=(0, 10), fill="x", padx=40)

def select_fixed_region(app):
    try:
        bbox = capture_rectangle()
        if not bbox or len(bbox) != 4:
            messagebox.showerror("Selection Error", "Failed to select a valid region.")
            return
        x1, y1, x2, y2 = map(int, bbox)
        app.fixed_region = (x1, y1, x2 - x1, y2 - y1)
        messagebox.showinfo("Region Selected", f"Fixed region set to: {app.fixed_region}")
    except Exception as e:
        messagebox.showerror("Selection Error", f"Failed to select region: {str(e)}")

def start_ocr_loop(app):
    if not app.api_key:
        messagebox.showerror("Missing API Key", "Please set your OpenAI API Key in Settings.")
        return
    if not app.fixed_region:
        messagebox.showerror("No Region", "Please select a fixed region first.")
        return
    app.client = OpenAI(api_key=app.api_key)
    app.ocr_looping = True
    threading.Thread(target=lambda: run_ocr_loop(app), daemon=True).start()

def run_ocr_loop(app):
    while app.ocr_looping:
        try:
            result = capture_and_ocr_translate_fixed(app.client, app.fixed_region)
            app.text_output.delete("0.0", "end")
            app.text_output.insert("0.0", result)
        except Exception as e:
            app.text_output.delete("0.0", "end")
            app.text_output.insert("0.0", f"❌ OCR Loop failed:\n{str(e)}")
            break
        time.sleep(5)

def stop_ocr_loop(app):
    app.ocr_looping = False
    app.text_output.delete("0.0", "end")
    app.text_output.insert("0.0", "OCR Loop stopped.")
