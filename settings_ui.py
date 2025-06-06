import customtkinter as ctk
from tkinter import messagebox
import json

def open_hotkey_capture_dialog(app, entry_hotkey):
    capture_win = ctk.CTkToplevel(app)
    capture_win.title("Press desired hotkey")
    capture_win.geometry("400x150")
    capture_win.grab_set()  # 模态

    pressed_keys = set()
    key_label = ctk.CTkLabel(capture_win, text="Please Press Keys...")
    key_label.pack(pady=20)

    def on_key_press(event):
        key_name = event.keysym.lower()

        # 转换常见修饰键名，确保 keyboard 库能识别
        if key_name in ("control_l", "control_r"):
            key_name = "ctrl"
        elif key_name in ("shift_l", "shift_r"):
            key_name = "shift"
        elif key_name in ("alt_l", "alt_r"):
            key_name = "alt"

        pressed_keys.add(key_name)
        key_label.configure(text=" + ".join(sorted(pressed_keys)))

    capture_win.bind("<KeyPress>", on_key_press)

    def confirm():
        if pressed_keys:
            new_hotkey = "+".join(sorted(pressed_keys))
            app.hotkey = new_hotkey
            entry_hotkey.configure(state="normal")
            entry_hotkey.delete(0, ctk.END)
            entry_hotkey.insert(0, new_hotkey)
            entry_hotkey.configure(state="readonly")

            import keyboard
            keyboard.clear_all_hotkeys()
            keyboard.add_hotkey(app.hotkey, app.hotkey_translate)

            capture_win.destroy()
        else:
            messagebox.showwarning("提示", "请至少按下一个键。")

    btn_confirm = ctk.CTkButton(capture_win, text="Confirm", command=confirm)
    btn_confirm.pack(pady=10)

    capture_win.focus_set()



def open_settings_window(app):
    import keyboard

    settings = ctk.CTkToplevel(app)
    settings.title("Settings")
    settings.geometry("400x350")

    # OpenAI API Key
    ctk.CTkLabel(settings, text="OpenAI API Key:").pack(pady=(15, 5))
    entry_key = ctk.CTkEntry(settings, show="*")
    entry_key.pack(pady=(0, 10), fill="x", padx=20)
    if app.api_key:
        entry_key.insert(0, app.api_key)

    # Translation Hotkey Label
    ctk.CTkLabel(settings, text="Translation Hotkey:").pack(pady=(10, 5))
    entry_hotkey = ctk.CTkEntry(settings)
    entry_hotkey.pack(pady=(0, 5), fill="x", padx=20)
    entry_hotkey.insert(0, app.hotkey)
    entry_hotkey.configure(state="readonly")  # 只读，不允许直接输入

    # 设置快捷键按钮
    btn_set_hotkey = ctk.CTkButton(settings, text="设置快捷键", 
                                  command=lambda: open_hotkey_capture_dialog(app, entry_hotkey))
    btn_set_hotkey.pack(pady=(0, 10), fill="x", padx=20)

    # Theme
    ctk.CTkLabel(settings, text="Theme:").pack(pady=(10, 5))
    combo_theme = ctk.CTkComboBox(settings, values=["System", "Light", "Dark"])
    combo_theme.pack(pady=(0, 10), fill="x", padx=20)
    combo_theme.set(app.theme)

    # Auto-detect Source Language
    frame_auto = ctk.CTkFrame(settings, fg_color="transparent")
    frame_auto.pack(pady=(10, 10), fill="x", padx=20)
    label_auto = ctk.CTkLabel(frame_auto, text="🔍 Auto-detect Source Language:")
    label_auto.pack(side="left")
    auto_var = ctk.BooleanVar(value=app.auto_detect)
    def toggle_language_state():
        if auto_var.get():
            app.combo_lang.configure(state="disabled")
        else:
            app.combo_lang.configure(state="normal")
    check_auto = ctk.CTkCheckBox(frame_auto, text="", variable=auto_var, command=toggle_language_state)
    check_auto.pack(side="left", padx=(10, 0))

    # Close to Tray option
    frame_minimize = ctk.CTkFrame(settings, fg_color="transparent")
    frame_minimize.pack(pady=(5, 10), fill="x", padx=20)
    label_minimize = ctk.CTkLabel(frame_minimize, text="🧩 Close to tray instead of exit:")
    label_minimize.pack(side="left")
    minimize_var = ctk.BooleanVar(value=app.minimize_on_close)
    check_minimize = ctk.CTkCheckBox(frame_minimize, text="", variable=minimize_var)
    check_minimize.pack(side="left", padx=(10, 0))

    # Save button
    def save_key():
        app.api_key = entry_key.get().strip()
        app.hotkey = entry_hotkey.get().strip()
        app.theme = combo_theme.get()
        app.auto_detect = auto_var.get()
        app.last_used_language = app.combo_lang.get()
        app.minimize_on_close = minimize_var.get()

        app.save_settings(
            app.api_key,
            app.hotkey,
            app.theme,
            app.auto_detect,
            app.last_used_language,
            app.minimize_on_close
        )

        from ui.utils import apply_theme
        apply_theme(app.theme)
        settings.destroy()

        keyboard.clear_all_hotkeys()
        keyboard.add_hotkey(app.hotkey, app.hotkey_translate)
        app.combo_lang.configure(state="disabled" if app.auto_detect else "normal")

    ctk.CTkButton(settings, text="Save", command=save_key).pack(pady=(5, 10), fill="x", padx=100)
