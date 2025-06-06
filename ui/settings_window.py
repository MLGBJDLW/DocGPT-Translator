import customtkinter as ctk
import keyboard

def open_settings_window(app):
    settings = ctk.CTkToplevel(app)
    settings.title("Settings")
    settings.geometry("400x300")

    ctk.CTkLabel(settings, text="OpenAI API Key:").pack(pady=(15, 5))
    entry_key = ctk.CTkEntry(settings, show="*")
    entry_key.pack(pady=(0, 10), fill="x", padx=20)
    if app.api_key: entry_key.insert(0, app.api_key)

    ctk.CTkLabel(settings, text="Translation Hotkey:").pack(pady=(10, 5))
    entry_hotkey = ctk.CTkEntry(settings)
    entry_hotkey.pack(pady=(0, 10), fill="x", padx=20)
    entry_hotkey.insert(0, app.hotkey)

    ctk.CTkLabel(settings, text="Theme:").pack(pady=(10, 5))
    combo_theme = ctk.CTkComboBox(settings, values=["System", "Light", "Dark"])
    combo_theme.pack(pady=(0, 10), fill="x", padx=20)
    combo_theme.set(app.theme)

    frame_auto = ctk.CTkFrame(settings, fg_color="transparent")
    frame_auto.pack(pady=(10, 10), fill="x", padx=20)
    label_auto = ctk.CTkLabel(frame_auto, text="🔍 Auto-detect Source Language:")
    label_auto.pack(side="left")
    auto_var = ctk.BooleanVar(value=app.auto_detect)

    check_auto = ctk.CTkCheckBox(frame_auto, text="", variable=auto_var)
    check_auto.pack(side="left", padx=(10, 0))

    def save_key():
        app.api_key = entry_key.get().strip()
        app.hotkey = entry_hotkey.get().strip()
        app.theme = combo_theme.get()
        app.auto_detect = auto_var.get()
        app.last_used_language = app.combo_lang.get()
        app.save_settings(app.api_key, app.hotkey, app.theme, app.auto_detect, app.last_used_language)
        ctk.set_appearance_mode(app.theme)
        settings.destroy()
        keyboard.clear_all_hotkeys()
        keyboard.add_hotkey(app.hotkey, app.hotkey_translate)

    ctk.CTkButton(settings, text="Save", command=save_key).pack(pady=(5, 10), fill="x", padx=100)
