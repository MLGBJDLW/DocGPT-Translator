import tkinter as tk

class SubtitleWindow:
    def __init__(self):
        self.root = tk.Toplevel()
        self.root.overrideredirect(True)  # 无边框
        self.root.attributes("-topmost", True)  # 始终置顶
        self.root.attributes("-alpha", 0.85)  # 透明度
        self.root.configure(bg="black")

        self.label = tk.Label(
            self.root, text="", font=("Microsoft YaHei", 18),
            fg="white", bg="black", wraplength=800, justify="left"
        )
        self.label.pack(padx=10, pady=10)

        # define window size and position
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width, height = 850, 100
        x = (screen_width - width) // 2
        y = screen_height - height - 80
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def update_text(self, text):
        self.label.config(text=text)
        self.root.update()

    def destroy(self):
        self.root.destroy()
