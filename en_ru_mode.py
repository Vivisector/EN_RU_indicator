from PIL import Image, ImageDraw
import pystray
import sys
import os
import tkinter as tk
import platform
import threading
# import time

import sys
import os

def resource_path(relative_path):
    """ Получает абсолютный путь к ресурсу, работает и для PyInstaller и для обычного запуска """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

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
        buffer = ctypes.create_unicode_buffer(9)
        ctypes.windll.kernel32.GetLocaleInfoW(
            lid, 0x00000003, buffer, len(buffer)
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
        self.visible = True
        self.alpha = 0.2
        self.position = 'bottom'

        self.root = tk.Tk()
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.attributes("-alpha", self.alpha)
        self.root.configure(bg='')

        self.label = tk.Label(
            self.root, text="", font=("Arial", 150), fg="white", bg="blue"
        )
        self.label.pack()

        self.root.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
        extended_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(
            hwnd, win32con.GWL_EXSTYLE,
            extended_style | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
        )

        self.update_position()
        self.update_layout()
        self.create_tray_icon()
        self.root.mainloop()

    def toggle_visibility(self, icon=None, item=None):
        if self.visible:
            self.root.withdraw()
        else:
            self.root.deiconify()
        self.visible = not self.visible
        self.icon.update_menu()

    def set_position(self, pos):
        self.position = pos

    def set_alpha(self, alpha_value):
        self.alpha = alpha_value
        self.root.attributes("-alpha", self.alpha)

    def create_tray_icon(self):

        # image = Image.new('RGB', (64, 64), color='blue')
        # draw = ImageDraw.Draw(image)
        # draw.text((10, 20), "L", fill="white")
        # Путь до вашей иконки (ICO или PNG)
        # icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')  # или 'icon.ico'
        icon_path = resource_path('icon.png')
        image = Image.open(icon_path)

        def dynamic_visibility_label(item):
            return "Скрыть" if self.visible else "Показать"

        menu = pystray.Menu(
            pystray.MenuItem(
                dynamic_visibility_label,
                self.toggle_visibility,
                default=True
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                'Положение',
                pystray.Menu(
                    pystray.MenuItem('Сверху', lambda: self.set_position('top'), checked=lambda item: self.position == 'top'),
                    pystray.MenuItem('Снизу', lambda: self.set_position('bottom'), checked=lambda item: self.position == 'bottom'),
                    pystray.MenuItem('Слева', lambda: self.set_position('left'), checked=lambda item: self.position == 'left'),
                    pystray.MenuItem('Справа', lambda: self.set_position('right'), checked=lambda item: self.position == 'right'),
                )
            ),
            pystray.MenuItem(
                'Прозрачность',
                pystray.Menu(
                    pystray.MenuItem('0.1', lambda: self.set_alpha(0.1), checked=lambda item: self.alpha == 0.1),
                    pystray.MenuItem('0.2', lambda: self.set_alpha(0.2), checked=lambda item: self.alpha == 0.2),
                    pystray.MenuItem('0.3', lambda: self.set_alpha(0.3), checked=lambda item: self.alpha == 0.3),
                )
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('Выход', self.quit_app)
        )

        self.icon = pystray.Icon("LayoutIndicator", image, "Layout Indicator", menu)
        threading.Thread(target=self.icon.run, daemon=True).start()

    def quit_app(self, _=None):
        self.icon.stop()
        self.root.destroy()
        sys.exit()

    def update_position(self):
        hwnd = win32gui.GetForegroundWindow()
        monitor = win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
        monitor_info = win32api.GetMonitorInfo(monitor)
        work_left, work_top, work_right, work_bottom = monitor_info['Work']

        window_width = 500
        window_height = 180

        if self.position == 'bottom':
            x = work_left + (work_right - work_left - window_width) // 2
            y = work_bottom - window_height - 10
        elif self.position == 'top':
            x = work_left + (work_right - work_left - window_width) // 2
            y = work_top + 10
        elif self.position == 'left':
            x = work_left + 10
            y = work_top + (work_bottom - work_top - window_height) // 2
        elif self.position == 'right':
            x = work_right - window_width - 10
            y = work_top + (work_bottom - work_top - window_height) // 2
        else:
            x = 100
            y = 100

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.after(500, self.update_position)

    def update_layout(self):
        try:
            layout = get_layout()
            self.label.config(text=layout)
        except Exception as e:
            print("Error in update_layout:", e)
        self.root.after(500, self.update_layout)


if __name__ == "__main__":
    LayoutOverlay()
