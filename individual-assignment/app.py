from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

from diagnostic_system import DiagnosticSystem


class DiagnosticApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Експертна система діагностики ПК")
        self.root.geometry("980x620")

        history_path = Path(__file__).with_name("diagnostic_history.csv")
        self.system = DiagnosticSystem(history_path)

        self.power_failure_var = tk.BooleanVar(value=False)
        self.fans_running_var = tk.StringVar(value="yes")
        self.temperature_var = tk.StringVar()
        self.noise_var = tk.BooleanVar(value=False)
        self.beep_var = tk.StringVar(value="no")
        self.fan_speed_var = tk.StringVar(value="normal")
        self.disk_var = tk.StringVar(value="yes")

        self._build_ui()
        self.refresh_history()

    def _build_ui(self) -> None:
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=12, pady=12)

        input_tab = ttk.Frame(notebook, padding=16)
        history_tab = ttk.Frame(notebook, padding=16)

        notebook.add(input_tab, text="Введення симптомів")
        notebook.add(history_tab, text="Історія діагнозів")

        self._build_input_tab(input_tab)
        self._build_history_tab(history_tab)

    def _build_input_tab(self, parent: ttk.Frame) -> None:
        title = ttk.Label(parent, text="Вкажіть симптоми ПК", font=("Arial", 16, "bold"))
        title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 16))

        ttk.Checkbutton(
            parent,
            text="Комп'ютер не вмикається",
            variable=self.power_failure_var,
        ).grid(row=1, column=0, sticky="w", pady=6)

        ttk.Label(parent, text="Чути вентилятори:").grid(row=2, column=0, sticky="w", pady=6)
        fans_frame = ttk.Frame(parent)
        fans_frame.grid(row=2, column=1, sticky="w", pady=6)
        ttk.Radiobutton(fans_frame, text="Так", variable=self.fans_running_var, value="yes").pack(side="left")
        ttk.Radiobutton(fans_frame, text="Ні", variable=self.fans_running_var, value="no").pack(side="left", padx=(8, 0))

        ttk.Label(parent, text="Температура CPU (°C):").grid(row=3, column=0, sticky="w", pady=6)
        ttk.Entry(parent, textvariable=self.temperature_var, width=18).grid(row=3, column=1, sticky="w", pady=6)

        ttk.Checkbutton(
            parent,
            text="Є сторонній шум",
            variable=self.noise_var,
        ).grid(row=4, column=0, sticky="w", pady=6)

        ttk.Label(parent, text="Сигнали BIOS:").grid(row=5, column=0, sticky="w", pady=6)
        beep_box = ttk.Combobox(parent, textvariable=self.beep_var, values=["yes", "no"], state="readonly", width=15)
        beep_box.grid(row=5, column=1, sticky="w", pady=6)

        ttk.Label(parent, text="Швидкість вентиляторів:").grid(row=6, column=0, sticky="w", pady=6)
        speed_box = ttk.Combobox(
            parent,
            textvariable=self.fan_speed_var,
            values=["low", "normal", "high"],
            state="readonly",
            width=15,
        )
        speed_box.grid(row=6, column=1, sticky="w", pady=6)

        ttk.Label(parent, text="Диск визначається BIOS/OS:").grid(row=7, column=0, sticky="w", pady=6)
        disk_box = ttk.Combobox(parent, textvariable=self.disk_var, values=["yes", "no"], state="readonly", width=15)
        disk_box.grid(row=7, column=1, sticky="w", pady=6)

        ttk.Button(parent, text="Отримати діагноз", command=self.run_diagnosis).grid(
            row=8, column=0, sticky="w", pady=(18, 12)
        )

        self.result_label = ttk.Label(parent, text="Результат: очікується введення симптомів.", wraplength=860, justify="left")
        self.result_label.grid(row=9, column=0, columnspan=2, sticky="w", pady=8)

    def _build_history_tab(self, parent: ttk.Frame) -> None:
        ttk.Button(parent, text="Оновити", command=self.refresh_history).pack(anchor="w", pady=(0, 12))

        columns = ("timestamp", "symptoms", "diagnosis")
        self.history_tree = ttk.Treeview(parent, columns=columns, show="headings", height=12)
        self.history_tree.heading("timestamp", text="Дата й час")
        self.history_tree.heading("symptoms", text="Симптоми")
        self.history_tree.heading("diagnosis", text="Діагноз")
        self.history_tree.column("timestamp", width=160, anchor="w")
        self.history_tree.column("symptoms", width=450, anchor="w")
        self.history_tree.column("diagnosis", width=320, anchor="w")

        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)

        self.history_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _collect_form_data(self) -> dict[str, object]:
        return {
            "power_failure": self.power_failure_var.get(),
            "fans_running": self.fans_running_var.get() == "yes",
            "temperature": self.temperature_var.get(),
            "noise_present": self.noise_var.get(),
            "beep_code": self.beep_var.get(),
            "fan_speed": self.fan_speed_var.get(),
            "disk_detected": self.disk_var.get(),
        }

    def run_diagnosis(self) -> None:
        raw_data = self._collect_form_data()

        try:
            diagnoses = self.system.diagnose(raw_data)
            self.system.save_record(raw_data, diagnoses)
        except ValueError as exc:
            messagebox.showerror("Помилка вводу", str(exc))
            return

        message = "\n".join(diagnoses)
        self.result_label.config(text=f"Результат:\n{message}")
        messagebox.showinfo("Діагноз", message)
        self.refresh_history()

    def refresh_history(self) -> None:
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        history = self.system.load_history(limit=10)
        for _, row in history.iterrows():
            self.history_tree.insert("", "end", values=(row["timestamp"], row["symptoms"], row["diagnosis"]))


def main() -> None:
    root = tk.Tk()
    app = DiagnosticApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
