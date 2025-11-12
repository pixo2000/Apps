# Methodentag Kurszuteilung - Web Interface

Ein modernes Web-Interface für die automatische Kurszuteilung beim Methodentag.

## Features

- 📊 Material Design 3 UI
- 🎯 Automatische Kurszuteilung basierend auf Schülerwünschen
- ⚙️ Konfigurierbare Optionen (Max. Kursgröße, Gleichverteilung)
- 📈 Detaillierte Statistiken und Visualisierungen
- 💾 Export als CSV und TXT

## Installation

1. Abhängigkeiten installieren:
```bash
pip install -r requirements.txt
```

2. Sicherstellen, dass die Datei `daten.csv` im gleichen Verzeichnis liegt

## Verwendung

### Web-Interface starten

```bash
python app.py
```

Dann im Browser öffnen: `http://localhost:5000`

### Kommandozeilen-Version

```bash
python main.py
```

## Workflow

1. **Daten analysieren**: Überprüfen Sie wie viele Schüler und Kurse vorhanden sind
2. **Konfiguration**: Legen Sie maximale Kursgröße und Verteilungsoptionen fest
3. **Zuteilung starten**: Führen Sie den Algorithmus aus
4. **Ergebnisse downloaden**: Laden Sie die generierten CSV/TXT Dateien herunter

## Generierte Dateien

- `zuteilung_schueler.csv` - Zuteilung pro Schüler
- `zuteilung_kurse.csv` - Übersicht pro Kurs
- `zusammenfassung.txt` - Detaillierte Statistiken

## Technologie

- Backend: Flask (Python)
- Frontend: HTML5, CSS3 (Material Design 3), Vanilla JavaScript
- Algorithmus: Iterative Zuteilung mit Constraint-Berücksichtigung
