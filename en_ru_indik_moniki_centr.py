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
        # print("Starting LayoutOverlay")
        self.root = tk.Tk()
        hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
        extended_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                               extended_style | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)

        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)

        # Устанавливаем прозрачность окна (от 0.1 до 1.0)
        self.root.attributes("-alpha", 0.1)

        # Убираем фон у окна
        self.root.configure(bg='')

        # Убираем фон у метки
        self.label = tk.Label(
            self.root, text="", font=("Arial", 320), fg="white", bg="blue"  # Для видимости
        )
        self.label.pack()

        self.update_position()
        self.update_layout()
        self.root.mainloop()

    def get_foreground_window_position(self):
        hwnd = win32gui.GetForegroundWindow()  # Получаем активное окно
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)  # Получаем его координаты
        return left, top, right, bottom

    def update_position(self):
        # Получаем координаты активного окна
        left, top, right, bottom = self.get_foreground_window_position()

        # Вычисляем размеры нашего окна (мы хотим его немного меньше активного окна)
        window_width = 900
        window_height = 400

        # Позиционируем индикатор поверх активного окна
        x = left + (right - left - window_width) // 2
        y = top + (bottom - top - window_height) // 2

        # Устанавливаем геометрию окна индикатора
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Повторно обновляем позицию через 1000 миллисекунд
        self.root.after(500, self.update_position)

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
