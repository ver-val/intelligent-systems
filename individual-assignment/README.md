# Експертна система діагностики ПК

## Запуск

```bash
cd individual-assignment
python3 -m pip install -r requirements.txt
python3 app.py
```

## Тести

```bash
cd individual-assignment
python3 -m pip install -r requirements.txt
python3 -m unittest -v
```

## Що реалізовано

- клас `DiagnosticSystem` з правилами, валідацією та історією в CSV через `pandas`
- GUI на `tkinter` із двома вкладками: введення симптомів та історія діагнозів
- збереження `timestamp`, симптомів і діагнозу в `diagnostic_history.csv`
- unit-тести логіки без GUI
