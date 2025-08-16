# Lanis Stundenplan Rechner

Eine Python-Anwendung, die sich mit dem Lanis Schulportal verbindet, den Vertretungsplan abruft und Stundenpläne für alle Klassen mit Raum- und Lehrerinformationen berechnet.

## Features

- 🔐 Sichere Anmeldung am Lanis Schulportal
- 📊 Automatisches Abrufen des Vertretungsplans
- 📅 Berechnung angepasster Stundenpläne für alle Klassen
- 🖥️ Benutzerfreundliche GUI-Oberfläche
- 💾 Export zu CSV für weitere Verarbeitung
- ⚙️ Sichere Speicherung von Zugangsdaten in .env-Datei

## Installation

1. **Repository klonen oder Dateien herunterladen**

2. **Python-Abhängigkeiten installieren:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Zugangsdaten konfigurieren:**
   - Öffne die `.env` Datei
   - Trage deine Lanis Schulportal Zugangsdaten ein:
     ```
     LANIS_USERNAME=dein_benutzername
     LANIS_PASSWORD=dein_passwort
     LANIS_SCHOOL_ID=deine_schul_id
     ```

## Verwendung

1. **Anwendung starten:**
   ```bash
   python main.py
   ```

2. **Anmeldung:**
   - Gehe zum "Anmeldung" Tab
   - Trage deine Zugangsdaten ein (oder sie werden automatisch aus der .env geladen)
   - Klicke "Anmelden"

3. **Daten laden:**
   - Gehe zum "Daten" Tab
   - Klicke "Vertretungsplan laden" um die aktuellen Vertretungen abzurufen
   - Klicke "Stundenplan laden" um die regulären Stundenpläne zu laden
   - Klicke "Berechnen" um die angepassten Stundenpläne zu erstellen

4. **Ergebnisse anzeigen:**
   - Gehe zum "Ergebnisse" Tab
   - Hier siehst du die berechneten Stundenpläne für alle Klassen
   - Exportiere die Daten mit "Nach CSV exportieren"

## Funktionsweise

### Datenabfrage
- Die Anwendung nutzt Selenium WebDriver um sich am Lanis Portal anzumelden
- Vertretungsplan und reguläre Stundenpläne werden von den entsprechenden Seiten abgerufen
- Die HTML-Daten werden mit BeautifulSoup geparst

### Stundenplan-Berechnung
- Reguläre Stundenpläne werden als Basis genommen
- Vertretungen werden entsprechend angewendet:
  - Lehrervertretungen
  - Raumänderungen
  - Fachvertretungen
  - Zusätzliche Stunden
  - Entfallende Stunden

### Datenexport
- Berechnet Stundenpläne können als CSV exportiert werden
- Format: Klasse, Datum, Zeit, Fach, Lehrer, Raum, Bemerkung

## Technische Details

### Abhängigkeiten
- `selenium`: Web-Automatisierung für Login und Datenabfrage
- `beautifulsoup4`: HTML-Parsing
- `requests`: HTTP-Requests
- `tkinter`: GUI-Framework
- `python-dotenv`: Umgebungsvariablen-Management

### Architektur
- `LanisPortalScraper`: Handhabt alle Interaktionen mit dem Lanis Portal
- `ScheduleCalculator`: Berechnet und verarbeitet Stundenplandaten
- `StundenplanGUI`: Hauptanwendung mit grafischer Benutzeroberfläche

## Sicherheit

- Zugangsdaten werden lokal in der `.env` Datei gespeichert
- Keine Übertragung von Zugangsdaten an Dritte
- WebDriver läuft im Headless-Modus (unsichtbar)

## Fehlerbehebung

### Login-Probleme
- Überprüfe Benutzername, Passwort und Schul-ID
- Stelle sicher, dass das Lanis Portal erreichbar ist
- Prüfe, ob dein Account nicht gesperrt ist

### Datenabfrage-Probleme
- Stelle sicher, dass du angemeldet bist
- Das Lanis Portal könnte seine Struktur geändert haben
- Überprüfe deine Internetverbindung

### Allgemeine Probleme
- Stelle sicher, dass Chrome Browser installiert ist (für Selenium)
- Überprüfe, ob alle Abhängigkeiten installiert sind
- Führe die Anwendung mit Administratorrechten aus, falls nötig

## Lizenz

Dieses Projekt ist für Bildungszwecke erstellt. Verwende es verantwortungsvoll und halte dich an die Nutzungsbedingungen des Lanis Schulportals.

## Autor

pixo2000 - August 2025

## Haftungsausschluss

Diese Anwendung ist nicht offiziell mit dem Lanis Schulportal verbunden. Verwende sie auf eigene Verantwortung und stelle sicher, dass du die Nutzungsbedingungen deiner Schule einhältst.
