import ctypes


def get_screen_size(default_width: int, default_height: int) -> tuple[int, int]:
    """
    Returns the primary display size with a safe fallback for headless cases.
    """
    try:
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        width = int(user32.GetSystemMetrics(0))
        height = int(user32.GetSystemMetrics(1))

        if width > 0 and height > 0:
            return width, height
    except Exception:
        pass

    try:
        import tkinter as tk

        root = tk.Tk()
        root.withdraw()
        width = int(root.winfo_screenwidth())
        height = int(root.winfo_screenheight())
        root.destroy()

        if width > 0 and height > 0:
            return width, height
    except Exception:
        pass

    return default_width, default_height
