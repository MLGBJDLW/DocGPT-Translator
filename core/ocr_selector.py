import tkinter as tk

def capture_rectangle():
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.attributes("-alpha", 0.3)
    root.configure(background='black')
    root.title("Drag to Capture Region")
    canvas = tk.Canvas(root, cursor="cross", bg="black")
    canvas.pack(fill=tk.BOTH, expand=True)

    rect = None
    start_x = start_y = 0
    coords = None  # Initialize with dummy values

    def on_mouse_down(event):
        nonlocal start_x, start_y, rect
        start_x, start_y = event.x, event.y
        rect = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline='red', width=2)

    def on_mouse_drag(event):
        canvas.coords(rect, start_x, start_y, event.x, event.y)

    def on_mouse_up(event):
        nonlocal coords
        coords = canvas.coords(rect)
        root.quit()
        root.destroy()
        
    def on_close(event = None):
        nonlocal coords
        coords = None
        root.quit()
        root.destroy()

    canvas.bind("<ButtonPress-1>", on_mouse_down)
    canvas.bind("<B1-Motion>", on_mouse_drag)
    canvas.bind("<ButtonRelease-1>", on_mouse_up)
    root.bind("<Escape>", on_close)  # Allow closing with Escape key
    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

    return coords if coords and len(coords) == 4 else None

