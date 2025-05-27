from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw

def create_tray_icon(app):
    image = Image.new('RGB', (64, 64), color=(40, 40, 40))
    draw = ImageDraw.Draw(image)
    draw.text((20, 20), "T", fill=(255, 255, 255))

    def on_show():
        app.deiconify()

    def on_quit(icon, item):
        icon.stop()
        app.quit()

    def set_target_language(lang):
        app.last_used_language = lang
        app.combo_lang.set(lang)
        app.save_settings(
            app.api_key,
            app.hotkey,
            app.theme,
            app.auto_detect,
            app.last_used_language,
            app.minimize_on_close
        )

    lang_items = [MenuItem(name, lambda _, lang=name: set_target_language(lang))
                  for name in app.combo_lang.cget("values")]

    menu = Menu(
        MenuItem('Show Translator', lambda: on_show()),
        MenuItem('Target Language', Menu(*lang_items)),
        MenuItem('Quit', on_quit)
    )
    icon = Icon("GPT Translator", image, "GPT Translator", menu)

    app.tray_icon = icon
    import threading
    threading.Thread(target=icon.run, daemon=True).start()