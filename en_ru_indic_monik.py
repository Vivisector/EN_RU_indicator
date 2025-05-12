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
        hwnd = win32gui.GetForegroundWindow()  # Получаем активное окно
        thread_id, _ = win32process.GetWindowThreadProcessId(hwnd)
        layout_id = win32api.GetKeyboardLayout(thread_id)
        lid = layout_id & (2 ** 16 - 1)

        # Получаем язык в виде строки: "EN", "RU", и т.д.
        buffer = ctypes.create_unicode_buffer(9)
        ctypes.windll.kernel32.GetLocaleInfoW(
            lid,
            0x00000003,  # LOCALE_SABBREVLANGNAME — возвращает "ENU", "RUS" и т.д.
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
        self.root = tk.Tk()
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.attributes("-alpha", 0.2)
        self.root.configure(bg='')

        # Убираем фон у метки
        self.label = tk.Label(
            self.root, text="", font=("Arial", 220), fg="white", bg="blue"  # Для видимости
        )
        self.label.pack()

        # Только теперь — получаем HWND и делаем окно "прозрачным для кликов"
        self.root.update_idletasks()  # Обновляем окно, чтобы hwnd стал доступен
        hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
        extended_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                               extended_style | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)

        self.update_position()
        # self.root.after(300, self.update_position)  # задержка 300 мс
        self.update_layout()
        self.root.mainloop()

    def get_foreground_window_position(self):
        hwnd = win32gui.GetForegroundWindow()  # Получаем активное окно
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)  # Получаем его координаты
        return left, top, right, bottom

    def update_position(self):
        hwnd = win32gui.GetForegroundWindow()
        monitor = win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
        monitor_info = win32api.GetMonitorInfo(monitor)
        work_area = monitor_info['Work']

        work_left, work_top, work_right, work_bottom = work_area

        window_width = 700
        window_height = 230

        # Центрируем по горизонтали в рамках текущего монитора
        x = work_left + (work_right - work_left - window_width) // 2
        y = work_bottom - window_height - 10  # отступ 50 пикселей от низа

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.after(500, self.update_position)

    def update_layout(self):
        try:
            layout = get_layout()
            # print("Layout is:", layout)
            self.label.config(text=layout)
        except Exception as e:
            print("Error in update_layout:", e)

        self.root.after(500, self.update_layout)

if __name__ == "__main__":
    LayoutOverlay()
