import tkinter as tk

class SubtitleWindow:
    def __init__(self):
        self.root = tk.Toplevel()
        self.root.title("Subtitles")
        self.root.overrideredirect(False)  # ❌ 取消原来的无边框，方便拖动和缩放
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.85)

        self.root.configure(bg="black")

        # 字幕 Label：横向显示，不换行，左对齐
        self.label = tk.Label(
            self.root, text="", font=("Microsoft YaHei", 18),
            fg="white", bg="black", wraplength=0, justify="left", anchor="w"
        )
        self.label.pack(expand=True, fill="both", padx=10, pady=10)

        # 设置默认窗口大小和位置
        width, height = 600, 120
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = screen_height - height - 60  # 距离底部60像素
        self.root.geometry(f"{width}x{height}+{x}+{y}")

        # 支持调整大小
        self.root.resizable(True, True)

        # 启用鼠标拖动移动
        self.label.bind("<ButtonPress-1>", self.start_move)
        self.label.bind("<B1-Motion>", self.do_move)

    def start_move(self, event):
        self._x = event.x
        self._y = event.y

    def do_move(self, event):
        x = self.root.winfo_x() + event.x - self._x
        y = self.root.winfo_y() + event.y - self._y
        self.root.geometry(f"+{x}+{y}")

    def update_text(self, text):
        single_line = " ".join(text.strip().splitlines())  # ❗ 合并多行
        self.label.config(text=single_line)
        self.root.update()

    def destroy(self):
        self.root.destroy()
