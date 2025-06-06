import tkinter as tk
import time
import threading
from openai import OpenAI
from core.ocr_handler import reader
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageOps
import numpy as np
import mss

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
    app.float_win.attributes("-topmost", True)
    app.float_win.configure(bg="#222222")

    app.float_dragging = False
    app.float_paused = False
    app.float_ocr_active = True

    container = tk.Frame(app.float_win, bg="#222222")
    container.pack(expand=True, fill="both")

    app.float_text = tk.Text(container, wrap="word", font=("Arial", 10),
                              bg="#222222", fg="#00FF99", insertbackground="#00FF99", relief="flat")
    app.float_text.pack(expand=True, fill="both", padx=10, pady=(10, 5))
    app.float_text.focus_set()

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

def grab_region(region):
    with mss.mss() as sct:
        monitor = {
            "top": region[1],
            "left": region[0],
            "width": region[2] - region[0],
            "height": region[3] - region[1]
        }
        sct_img = sct.grab(monitor)
        return Image.frombytes("RGB", sct_img.size, sct_img.rgb)

def enhance_image(img):
    gray = img.convert("L")
    inverted = ImageOps.invert(gray)
    enhanced = ImageOps.autocontrast(inverted)
    return enhanced

def run_floating_ocr_loop(app):
    while getattr(app, "float_ocr_active", False):
        if not getattr(app, "float_paused", False):
            try:
                if not (hasattr(app, "float_win") and app.float_win.winfo_exists()):
                    break

                x = app.float_win.winfo_rootx()
                y = app.float_win.winfo_rooty()
                w = app.float_win.winfo_width()
                h = app.float_win.winfo_height()
                region = (x, y, x + w, y + int(h * 0.85))

                screenshot = grab_region(region)
                if screenshot is None:
                    raise ValueError("Screenshot is empty")

                img = enhance_image(screenshot)
                img_np = np.array(img)
                if img_np.size == 0:
                    raise ValueError("Image is empty")

                results = reader.readtext(img_np)
                text = "\n".join([r[1] for r in results])

                if hasattr(app, "float_text") and app.float_text.winfo_exists():
                    app.float_text.delete("1.0", "end")
                    app.float_text.insert("1.0", text or "❌ No text detected.")
            except Exception as e:
                if hasattr(app, "float_text") and app.float_text.winfo_exists():
                    app.float_text.delete("1.0", "end")
                    app.float_text.insert("1.0", f"❌ Error:\n{e}")
                break
        time.sleep(2)

def close_floating_ocr(app):
    app.float_ocr_active = False
    if hasattr(app, "float_win"):
        app.float_win.destroy()
