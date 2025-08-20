# News Boarder

[Kalender-Link](https://start.schulportal.hessen.de/kalender.php?a=ical&i=5214&export=ical&t=47398d6bf42ddcd5ef343c4ea5b11d43b6e8da0521c802b72a5c5a9d789ec66050290985756de16055299d2b38e37ea0d38d1fe7ffdda667287a46110829c439)

## Funktionen

### Automatische Effektverteilung

Aus einem Ordner bei Windows werden alle Effekte gezogen und automatisch bei programmstart in einen nutzerspezifischen AppData Folder gelegt.

Das wird erst mal ignoriert, weil das andere wichtiger ist

### Automatisches NewsBoard ✅

Vom Kalender werden die ersten X Termine gezeigt und man kann bis zu vier auswählen. das entsprechende News Board wird generiert und ablegegt. Das Template ist hier im ordner

**Implementiert:**
- CustomTkinter GUI für Benutzerinteraktion
- iCal Parser für Kalender-Events
- Event-Auswahl (max. 4 Termine)
- Template-Verarbeitung mit automatischer Textersetzung
- Export als .setting Datei für DaVinci Resolve

**Features:**
- Lädt Termine automatisch vom Schulportal
- Zeigt nur zukünftige Termine an
- Formatiert Datumsangaben automatisch
- Generiert Überschrift mit Monatsnamen
- Begrenzt Event-Titel auf 30 Zeichen

**Installation:**
```bash
pip install -r requirements.txt
python main.py
```

### notes

fixen das der kram gekürzt wird
