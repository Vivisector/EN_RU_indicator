import tkinter as tk
import platform
import threading
import time

if platform.system() == "Windows":
    import win32api
    import win32con
    import win32gui
    import win32process
    import ctypes


    def get_layout():
        hwnd = win32gui.GetForegroundWindow()
        thread_id, _ = win32process.GetWindowThreadProcessId(hwnd)
        layout_id = win32api.GetKeyboardLayout(thread_id)
        lid = layout_id & (2 ** 16 - 1)

        # Получаем язык в виде строки: "EN", "RU", и т.д.
        buffer = ctypes.create_unicode_buffer(9)
        ctypes.windll.kernel32.GetLocaleInfoW(
            lid,
            # 0x00000002,  # LOCALE_SISO639LANGNAME
            0x00000003, # LOCALE_SABBREVLANGNAME — возвращает "ENU", "RUS" и т.д.

            buffer,
            len(buffer)
        )
        return buffer.value.upper()


elif platform.system() == "Linux":
    from xkbgroup import XKeyboard

    xk = XKeyboard()
    def get_layout():
        return xk.group_name.upper()

else:
    def get_layout():
        return "N/A"


class LayoutOverlay:
    def __init__(self):
        print("Starting LayoutOverlay")
        self.root = tk.Tk()
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.attributes("-alpha", 0.1)

        self.label = tk.Label(
            self.root, text="", font=("Arial", 320), fg="white", bg='blue'
        )
        self.label.pack()

        self.update_position()
        self.update_layout()
        self.root.mainloop()

    def update_position(self):
        window_width = 900
        window_height = 300
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def update_layout(self):
        try:
            layout = get_layout()
            print("Layout is:", layout)
            self.label.config(text=layout)
        except Exception as e:
            print("Error in update_layout:", e)

        self.root.after(500, self.update_layout)

if __name__ == "__main__":
    LayoutOverlay()
