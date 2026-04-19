from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
from typing import Any, Callable

import pandas as pd
from pandas.errors import EmptyDataError


Rule = tuple[Callable[[dict[str, Any]], bool], str]


@dataclass
class ValidationResult:
    valid_data: dict[str, Any]
    errors: list[str]


class DiagnosticSystem:
    def __init__(self, csv_path: str | Path = "diagnostic_history.csv") -> None:
        self.csv_path = Path(csv_path)
        self.rules: list[Rule] = [
            (
                lambda data: data["power_failure"]
                and not data["fans_running"]
                and not data["noise_present"],
                "Можливо несправний блок живлення або кабель живлення.",
            ),
            (
                lambda data: data["power_failure"]
                and data["fans_running"]
                and (data["beep_code"] == "yes" or data["noise_present"]),
                "Можлива проблема з оперативною пам'яттю або материнською платою.",
            ),
            (
                lambda data: data["power_failure"]
                and data["fans_running"]
                and data["beep_code"] == "no"
                and not data["noise_present"],
                "Можлива проблема з відеокартою, монітором або запуском материнської плати.",
            ),
            (
                lambda data: (not data["power_failure"])
                and data["fans_running"]
                and data["temperature"] >= 85,
                "Можливий перегрів процесора або забруднення системи охолодження.",
            ),
            (
                lambda data: (not data["power_failure"])
                and (not data["fans_running"] or data["fan_speed"] == "low")
                and data["temperature"] >= 70,
                "Можлива несправність вентилятора або проблеми з охолодженням.",
            ),
            (
                lambda data: (not data["power_failure"])
                and data["disk_detected"] == "no"
                and (not data["noise_present"] or data["beep_code"] == "yes"),
                "Можливо накопичувач не визначається або пошкоджене підключення диска.",
            ),
            (
                lambda data: (not data["power_failure"])
                and data["fans_running"]
                and data["temperature"] < 85
                and (data["noise_present"] or data["beep_code"] == "yes"),
                "Можливі збої під час запуску або сторонній шум від кулера, диска чи інших компонентів.",
            ),
        ]

    def validate_data(self, raw_data: dict[str, Any]) -> ValidationResult:
        errors: list[str] = []
        validated: dict[str, Any] = {
            "power_failure": bool(raw_data.get("power_failure", False)),
            "fans_running": bool(raw_data.get("fans_running", False)),
            "noise_present": bool(raw_data.get("noise_present", False)),
            "beep_code": str(raw_data.get("beep_code", "no")).strip().lower(),
            "fan_speed": str(raw_data.get("fan_speed", "normal")).strip().lower(),
            "disk_detected": str(raw_data.get("disk_detected", "yes")).strip().lower(),
        }

        if validated["beep_code"] not in {"yes", "no"}:
            errors.append("Поле 'Сигнали BIOS' має бути 'yes' або 'no'.")

        if validated["fan_speed"] not in {"low", "normal", "high"}:
            errors.append("Поле 'Швидкість вентиляторів' має бути low, normal або high.")

        if validated["disk_detected"] not in {"yes", "no"}:
            errors.append("Поле 'Диск визначається' має бути 'yes' або 'no'.")

        temperature_raw = str(raw_data.get("temperature", "")).strip()
        if not temperature_raw:
            errors.append("Поле 'Температура' є обов'язковим.")
        else:
            try:
                validated["temperature"] = float(temperature_raw)
            except ValueError:
                errors.append("Поле 'Температура' має бути числом.")

        return ValidationResult(valid_data=validated, errors=errors)

    def diagnose(self, raw_data: dict[str, Any]) -> list[str]:
        validation = self.validate_data(raw_data)
        if validation.errors:
            raise ValueError("\n".join(validation.errors))

        diagnoses: list[str] = []
        for condition, diagnosis in self.rules:
            if condition(validation.valid_data):
                diagnoses.append(diagnosis)

        return diagnoses or ["Невідомо: жодне правило не спрацювало, потрібна додаткова перевірка."]

    def save_record(self, raw_data: dict[str, Any], diagnoses: list[str]) -> None:
        validation = self.validate_data(raw_data)
        if validation.errors:
            raise ValueError("\n".join(validation.errors))

        record = pd.DataFrame(
            [
                {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "symptoms": json.dumps(validation.valid_data, ensure_ascii=False),
                    "diagnosis": " | ".join(diagnoses),
                }
            ]
        )

        self.csv_path.parent.mkdir(parents=True, exist_ok=True)
        file_exists = self.csv_path.exists() and self.csv_path.stat().st_size > 0
        record.to_csv(self.csv_path, mode="a", header=not file_exists, index=False)

    def load_history(self, limit: int = 10) -> pd.DataFrame:
        if not self.csv_path.exists() or self.csv_path.stat().st_size == 0:
            return pd.DataFrame(columns=["timestamp", "symptoms", "diagnosis"])

        try:
            history = pd.read_csv(self.csv_path)
        except EmptyDataError:
            return pd.DataFrame(columns=["timestamp", "symptoms", "diagnosis"])
        return history.tail(limit).reset_index(drop=True)
