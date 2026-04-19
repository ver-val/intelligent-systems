from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from diagnostic_system import DiagnosticSystem


class DiagnosticSystemTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.history_path = Path(self.temp_dir.name) / "history.csv"
        self.system = DiagnosticSystem(self.history_path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_power_supply_rule(self) -> None:
        diagnoses = self.system.diagnose(
            {
                "power_failure": True,
                "fans_running": False,
                "temperature": "25",
                "noise_present": False,
                "beep_code": "no",
                "fan_speed": "low",
                "disk_detected": "yes",
            }
        )
        self.assertIn("Можливо несправний блок живлення або кабель живлення.", diagnoses)

    def test_overheating_rule(self) -> None:
        diagnoses = self.system.diagnose(
            {
                "power_failure": False,
                "fans_running": True,
                "temperature": "92",
                "noise_present": True,
                "beep_code": "no",
                "fan_speed": "high",
                "disk_detected": "yes",
            }
        )
        self.assertIn("Можливий перегрів процесора або забруднення системи охолодження.", diagnoses)

    def test_boot_problem_rule(self) -> None:
        diagnoses = self.system.diagnose(
            {
                "power_failure": True,
                "fans_running": True,
                "temperature": "35",
                "noise_present": False,
                "beep_code": "no",
                "fan_speed": "normal",
                "disk_detected": "yes",
            }
        )
        self.assertIn("Можлива проблема з відеокартою, монітором або запуском материнської плати.", diagnoses)

    def test_multiple_diagnoses_are_returned(self) -> None:
        diagnoses = self.system.diagnose(
            {
                "power_failure": False,
                "fans_running": False,
                "temperature": "88",
                "noise_present": False,
                "beep_code": "no",
                "fan_speed": "low",
                "disk_detected": "no",
            }
        )
        self.assertGreaterEqual(len(diagnoses), 2)

    def test_invalid_temperature_raises_error(self) -> None:
        with self.assertRaises(ValueError):
            self.system.diagnose(
                {
                    "power_failure": False,
                    "fans_running": True,
                    "temperature": "abc",
                    "noise_present": False,
                    "beep_code": "no",
                    "fan_speed": "normal",
                    "disk_detected": "yes",
                }
            )

    def test_save_and_load_history(self) -> None:
        sample = {
            "power_failure": False,
            "fans_running": True,
            "temperature": "74",
            "noise_present": False,
            "beep_code": "no",
            "fan_speed": "normal",
            "disk_detected": "yes",
        }
        diagnoses = self.system.diagnose(sample)
        self.system.save_record(sample, diagnoses)

        history = self.system.load_history(limit=5)
        self.assertEqual(len(history), 1)
        self.assertIn("timestamp", history.columns)
        self.assertIn("symptoms", history.columns)
        self.assertIn("diagnosis", history.columns)

    def test_unknown_result_is_explicit(self) -> None:
        diagnoses = self.system.diagnose(
            {
                "power_failure": False,
                "fans_running": True,
                "temperature": "45",
                "noise_present": False,
                "beep_code": "no",
                "fan_speed": "normal",
                "disk_detected": "yes",
            }
        )
        self.assertEqual(
            diagnoses,
            ["Невідомо: жодне правило не спрацювало, потрібна додаткова перевірка."],
        )


if __name__ == "__main__":
    unittest.main()
