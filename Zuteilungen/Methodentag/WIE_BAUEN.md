# So baust du die macOS App

## 🎯 Einfachste Methode: GitHub Actions (Automatisch!)

Ich habe einen GitHub Workflow erstellt, der die App automatisch baut.

### Schritt für Schritt:

1. **Pushe deine Änderungen zu GitHub:**
   ```bash
   git add .
   git commit -m "Add macOS build setup"
   git push
   ```

2. **GitHub baut die App automatisch!** 🎉
   - Gehe zu: https://github.com/pixo2000/Apps/actions
   - Warte ~5 Minuten
   - Die App wird automatisch gebaut

3. **Lade die App herunter:**
   - Klicke auf den neuesten Workflow Run
   - Unter "Artifacts" findest du: `Methodentag-macOS-App`
   - Download → ZIP entpacken → fertig!

### Oder manuell starten:
- Gehe zu: https://github.com/pixo2000/Apps/actions
- Wähle "Build macOS App"
- Klick "Run workflow"

---

## 🖥️ Alternative: Auf einem echten Mac bauen

Falls du Zugang zu einem Mac hast:

1. **Projekt auf den Mac holen:**
   ```bash
   git clone https://github.com/pixo2000/Apps.git
   cd Apps/Zuteilungen/Methodentag
   ```

2. **Python installieren** (falls nicht vorhanden):
   - Download: https://www.python.org/downloads/macos/
   - Oder via Homebrew: `brew install python`

3. **App bauen:**
   ```bash
   pip install -r requirements.txt
   ./build_mac.sh
   ```

4. **Fertig!**
   - App liegt in: `dist/Methodentag Zuteilung.app`

---

## 📦 Was passiert beim Build?

- PyInstaller packt:
  - Python Interpreter
  - Alle Bibliotheken (Flask, pandas, etc.)
  - Deine Templates und Daten
  - → Eine einzelne `.app` Datei

- Größe: ~50-100 MB
- Die Lehrerin braucht **nur diese eine Datei**!

---

## ⚠️ Wichtig!

Nach dem Download muss die Lehrerin beim **ersten Start**:
1. Rechtsklick auf die App
2. "Öffnen" wählen
3. Bestätigen

(macOS Sicherheitseinstellung für Apps von "nicht verifizierten" Entwicklern)

---

## 🐛 Probleme?

### GitHub Actions schlagen fehl?
- Prüfe die Logs unter "Actions"
- Schreib mir die Fehlermeldung

### App startet nicht auf dem Mac?
- Terminal öffnen und eingeben:
   ```bash
   xattr -cr "/pfad/zur/Methodentag Zuteilung.app"
   ```
