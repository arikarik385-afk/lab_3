import math


# ==========================================
# ИНКАПСУЛЯЦИЯ, НАСЛЕДОВАНИЕ И ПОЛИМОРФИЗМ (МОДЕЛЬ)
# ==========================================

class Motor:
    """Базовый класс привода."""

    def __init__(self, name, max_speed=10.0):
        self.name = name
        self.max_speed = max_speed
        self._target_speed = 0.0  # Защищенный атрибут
        self.speed = 0.0
        self.angle = 0.0

    # Инкапсуляция: проверка значения при записи
    @property
    def target_speed(self):
        return self._target_speed

    @target_speed.setter
    def target_speed(self, value):
        if not 0.0 <= value <= self.max_speed:
            raise ValueError(f"Скорость должна быть в диапазоне 0...{self.max_speed} рад/с")
        self._target_speed = value

    # Полиморфизм: метод для переопределения
    def update(self, dt):
        raise NotImplementedError("Метод update() должен быть переопределён")

    def reset(self):
        self._target_speed = 0.0
        self.speed = 0.0
        self.angle = 0.0

    def __str__(self):
        return (f"{self.name}: скорость={self.speed:.2f} рад/с, "
                f"угол={math.degrees(self.angle):.1f}°")


# Наследование
class DCMotor(Motor):
    """Двигатель постоянного тока."""

    def __init__(self, name, max_speed=10.0, k=2.0):
        super().__init__(name, max_speed)  # Вызов базового класса
        self.k = k

    # Полиморфизм
    def update(self, dt):
        self.speed += (self._target_speed - self.speed) * self.k * dt
        self.angle += self.speed * dt


# Наследование
class StepperMotor(Motor):
    """Шаговый двигатель."""

    def __init__(self, name, max_speed=10.0, step_angle=math.radians(5)):
        super().__init__(name, max_speed)
        self.step_angle = step_angle
        self._accum = 0.0

    # Полиморфизм
    def update(self, dt):
        self._accum += self._target_speed * dt
        steps = int(self._accum / self.step_angle)
        self.angle += steps * self.step_angle
        self._accum -= steps * self.step_angle
        self.speed = (steps * self.step_angle) / dt


# ==========================================
# ИНТЕРФЕЙС (ГРАФИЧЕСКОЕ ОКНО)
# ==========================================

import tkinter as tk
from tkinter import ttk, messagebox


class MotorApp(tk.Tk):
    """Главное окно приложения (наследник tk.Tk)."""

    SIZE = 560
    DT = 0.05
    RADIUS = 200
    BG_MAIN = "#1e2230"
    BG_PANEL = "#2a2f42"
    BG_CANVAS = "#12151f"
    FG_TEXT = "#e6e9f2"
    FG_MUTED = "#8a93a8"
    ACCENT = "#4fc3f7"
    ACCENT2 = "#ff5252"
    OK = "#69f0ae"

    def __init__(self, motor):
        super().__init__()
        self.title("Motor Drive Control · variant 13")
        self.resizable(False, False)
        self.configure(bg=self.BG_MAIN)

        self.motor = motor
        self.running = False
        self._pulse = 0.0

        self.speed_var = tk.DoubleVar(value=0.0)
        self.info_var = tk.StringVar()

        self._setup_style()
        self._build_widgets()
        self._redraw()
        self.after(int(self.DT * 1000), self._tick)

    def _setup_style(self):
        """Настройка цветов и шрифтов."""
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TFrame", background=self.BG_PANEL)
        style.configure("TLabel", background=self.BG_PANEL, foreground=self.FG_TEXT, font=("Segoe UI", 10))
        style.configure("TButton", background=self.BG_MAIN, foreground=self.FG_TEXT, borderwidth=0,
                        font=("Segoe UI", 10, "bold"))
        style.map("TButton", background=[("active", self.ACCENT), ("pressed", self.ACCENT2)],
                  foreground=[("active", self.BG_MAIN), ("pressed", "white")])
        style.configure("Accent.TButton", background=self.ACCENT, foreground=self.BG_MAIN)
        style.map("Accent.TButton", background=[("active", self.OK), ("pressed", self.ACCENT2)],
                  foreground=[("active", self.BG_MAIN), ("pressed", "white")])
        style.configure("TCombobox", fieldbackground=self.BG_MAIN, background=self.BG_MAIN, foreground=self.FG_TEXT,
                        arrowcolor=self.ACCENT)
        style.configure("Horizontal.TScale", background=self.BG_PANEL, troughcolor=self.BG_MAIN, borderwidth=0)
        style.configure("Horizontal.TProgressbar", background=self.ACCENT, troughcolor=self.BG_MAIN, borderwidth=0,
                        lightcolor=self.ACCENT, darkcolor=self.ACCENT)

    def _build_widgets(self):
        """Создание элементов управления."""
        wrap = tk.Frame(self, bg=self.BG_MAIN)
        wrap.pack(padx=14, pady=14)

        self.canvas = tk.Canvas(wrap, width=self.SIZE, height=self.SIZE, bg=self.BG_CANVAS, highlightthickness=0)
        self.canvas.grid(row=0, column=0, rowspan=2, padx=(0, 14))

        panel = tk.Frame(wrap, bg=self.BG_PANEL, padx=10, pady=10)
        panel.grid(row=0, column=1, sticky="n")

        tk.Label(panel, text="MOTOR CONTROL", bg=self.BG_PANEL, fg=self.ACCENT, font=("Segoe UI", 12, "bold")).pack(
            anchor="w", pady=(0, 10))

        tk.Label(panel, text="Тип привода", bg=self.BG_PANEL, fg=self.FG_MUTED, font=("Segoe UI", 9)).pack(anchor="w",
                                                                                                           pady=(0, 2))
        self.motor_type = ttk.Combobox(panel, state="readonly", width=26, values=["DCMotor", "StepperMotor"])
        self.motor_type.set(type(self.motor).__name__)
        self.motor_type.pack(fill="x")
        self.motor_type.bind("<<ComboboxSelected>>", self._on_type_change)

        tk.Label(panel, text="Задание скорости, рад/с", bg=self.BG_PANEL, fg=self.FG_MUTED, font=("Segoe UI", 9)).pack(
            anchor="w", pady=(14, 2))
        self.speed_lbl = tk.Label(panel, text="0.00", bg=self.BG_PANEL, fg=self.ACCENT, font=("Consolas", 14, "bold"))
        self.speed_lbl.pack(anchor="e")
        ttk.Scale(panel, from_=0.0, to=self.motor.max_speed, length=220, variable=self.speed_var,
                  command=self._on_speed).pack(fill="x", pady=(0, 12))

        ttk.Button(panel, text="СТАРТ / СТОП", style="Accent.TButton", command=self._toggle).pack(fill="x", pady=4)
        ttk.Button(panel, text="СБРОС", command=self._reset).pack(fill="x", pady=4)

        tk.Label(panel, text="Фактическая скорость", bg=self.BG_PANEL, fg=self.FG_MUTED, font=("Segoe UI", 9)).pack(
            anchor="w", pady=(14, 2))
        self.speed_bar = ttk.Progressbar(panel, maximum=self.motor.max_speed, length=220)
        self.speed_bar.pack(fill="x")

        self.status_lbl = tk.Label(panel, text="● ОСТАНОВЛЕН", bg=self.BG_PANEL, fg=self.FG_MUTED,
                                   font=("Segoe UI", 10, "bold"))
        self.status_lbl.pack(anchor="w", pady=(20, 0))

        bottom = tk.Frame(wrap, bg=self.BG_MAIN)
        bottom.grid(row=1, column=1, sticky="we", pady=(10, 0))
        tk.Label(bottom, textvariable=self.info_var, bg=self.BG_MAIN, fg=self.FG_TEXT, font=("Consolas", 10),
                 anchor="w").pack(fill="x")

    # ==========================================
    # ОБРАБОТЧИКИ СОБЫТИЙ
    # ==========================================

    def _on_speed(self, value):
        """Обработка ползунка (с try/except)."""
        try:
            self.motor.target_speed = float(value)
        except ValueError as err:
            messagebox.showerror("Ошибка", str(err))
        self.speed_lbl.config(text=f"{float(value):.2f}")

    def _on_type_change(self, event):
        """Смена типа двигателя."""
        new_type = self.motor_type.get()
        if new_type == "DCMotor":
            self.motor = DCMotor("DC-1", max_speed=10.0, k=2.0)
        else:
            self.motor = StepperMotor("STEP-1", max_speed=10.0)

        self.speed_var.set(0.0)
        self.speed_lbl.config(text="0.00")
        self.speed_bar.config(maximum=self.motor.max_speed)
        self.running = False
        self.status_lbl.config(text="● ОСТАНОВЛЕН", fg=self.FG_MUTED)
        self._redraw()

    def _toggle(self):
        """Кнопка Старт/Стоп."""
        self.running = not self.running
        if self.running:
            self.status_lbl.config(text="● РАБОТАЕТ", fg=self.OK)
        else:
            self.status_lbl.config(text="● ОСТАНОВЛЕН", fg=self.FG_MUTED)

    def _reset(self):
        """Кнопка Сброс."""
        self.running = False
        self.motor.reset()
        self.speed_var.set(0.0)
        self.speed_lbl.config(text="0.00")
        self.status_lbl.config(text="● ОСТАНОВЛЕН", fg=self.FG_MUTED)
        self._redraw()

    # ==========================================
    # ТАЙМЕР И ГРАФИКА (CANVAS)
    # ==========================================

    def _tick(self):
        """Шаг таймера."""
        if self.running:
            self.motor.update(self.DT)  # Полиморфизм в действии
            self._pulse += self.DT * 6
        self._redraw()
        self.after(int(self.DT * 1000), self._tick)  # Безопасный таймер

    def _redraw(self):
        """Перерисовка холста."""
        cv = self.canvas
        cv.delete("all")
        c = self.SIZE / 2
        r = self.RADIUS

        cv.create_oval(c - r - 20, c - r - 20, c + r + 20, c + r + 20, outline="#232838", width=1)
        cv.create_oval(c - r, c - r, c + r, c + r, outline="#3a4258", width=3, fill="#171b27")

        for deg in range(0, 360, 10):
            a = math.radians(deg)
            length = 14 if deg % 30 == 0 else 7
            color = self.ACCENT if deg % 90 == 0 else "#3a4258"
            x1 = c + (r - 4) * math.cos(a)
            y1 = c - (r - 4) * math.sin(a)
            x2 = c + (r - 4 - length) * math.cos(a)
            y2 = c - (r - 4 - length) * math.sin(a)
            cv.create_line(x1, y1, x2, y2, fill=color, width=2)

        a = self.motor.angle
        glow = 4 + (2 * math.sin(self._pulse)) if self.running else 0
        x = c + r * 0.82 * math.cos(a)
        y = c - r * 0.82 * math.sin(a)

        cv.create_line(c, c, x, y, width=10, fill="#2a3348", arrow="last", arrowshape=(18, 22, 8))
        cv.create_line(c, c, x, y, width=5, fill=self.ACCENT2, arrow="last", arrowshape=(16, 20, 7))

        cv.create_oval(c - 14 - glow, c - 14 - glow, c + 14 + glow, c + 14 + glow, fill="#232838", outline=self.ACCENT,
                       width=2)
        cv.create_oval(c - 6, c - 6, c + 6, c + 6, fill=self.ACCENT)

        cv.create_text(c, 18, text="ROTOR", fill=self.FG_MUTED, font=("Segoe UI", 9, "bold"))
        cv.create_text(c, self.SIZE - 18, text=f"{math.degrees(self.motor.angle) % 360:5.1f}°", fill=self.ACCENT,
                       font=("Consolas", 16, "bold"))
        cv.create_text(c, 48, text=f"{self.motor.speed:5.2f} рад/с", fill=self.FG_TEXT, font=("Consolas", 11))

        self.speed_bar["value"] = self.motor.speed
        self.info_var.set(str(self.motor))


# ==========================================
# ГЛАВНАЯ ФУНКЦИЯ
# ==========================================

def main():
    """Запуск программы."""
    motor = DCMotor("DC-1", max_speed=10.0, k=2.0)
    app = MotorApp(motor)
    app.mainloop()


if __name__ == "__main__":
    main()