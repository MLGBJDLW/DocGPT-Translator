import customtkinter as ctk
from tkinter import messagebox
import threading
import time
from core.ocr_selector import capture_rectangle
from core.ocr_handler import capture_and_ocr_translate_fixed, capture_text_only
from ui.subtitles_window import SubtitleWindow
from openai import OpenAI

def build_fixed_ocr_tab(app):
    app.fixed_region = None
    app.ocr_looping = False
    app.subtitles_window = None  # 初始化为空

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
    app.subtitles_window = SubtitleWindow()
    app._last_ocr_text = ""
    threading.Thread(target=lambda: run_ocr_loop(app), daemon=True).start()
    
def clean_subtitle_output(text: str) -> str:
    lines = text.strip().splitlines()
    filtered = []
    for line in lines:
        if (
            line.lower().startswith("[detected:")
            or line.strip().lower().startswith("text:")
            or "似乎是" in line
            or "检测" in line
            or "抱歉" in line
        ):
            continue
        filtered.append(line.strip())
    return "\n".join(filtered).strip()

def run_ocr_loop(app):
    while app.ocr_looping:
        try:
            raw_text = capture_text_only(app.fixed_region).strip()

            # 🔒 排除空文本
            if not raw_text:
                print("[OCR] Empty result, skipping...")
                time.sleep(0.5)
                continue

            # 🔁 跳过重复内容
            if raw_text == app._last_ocr_text:
                print("[OCR] Same as last result, skipping...")
                time.sleep(0.5)
                continue

            # ✅ 内容变了，保存
            app._last_ocr_text = raw_text

            # 🎯 执行翻译
            result = capture_and_ocr_translate_fixed(app.client, app.fixed_region)

            # 更新文本区域
            app.text_output.delete("0.0", "end")
            app.text_output.insert("0.0", result)

            # 更新字幕窗口
            if app.subtitles_window:
                cleaned_result = clean_subtitle_output(result)
                app.subtitles_window.update_text(cleaned_result)

        except Exception as e:
            print("[OCR ERROR]", e)
            app.text_output.delete("0.0", "end")
            app.text_output.insert("0.0", f"❌ OCR Loop failed:\n{str(e)}")
            break

        time.sleep(0.5)


def stop_ocr_loop(app):
    app.ocr_looping = False
    if app.subtitles_window:
        app.subtitles_window.destroy()
        app.subtitles_window = None
    app.text_output.delete("0.0", "end")
    app.text_output.insert("0.0", "OCR Loop stopped.")

__all__ = [
    "build_fixed_ocr_tab",
    'stop_ocr_loop']
