# Valorant Raph Cup - Discord Bot

Ein Discord Bot für automatisierte Turnieranmeldungen mit Valorant-Integration.

## Features

### 🏆 Cup-Ankündigung
- Hauptnachricht mit aktuellem Cup-Datum oder Siegerteam
- Zwei Buttons: **Regeln** und **Anmelden**
- Automatische Updates bei neuen Votes

### 📋 Anmeldesystem
- Modal-Dialog für Valorant Name + Tag
- Automatische Rank-Abfrage über henrikdev API
- Zeigt aktuellen und höchsten Rank
- Maximale Spielerzahl: 10/16/20 (automatische Anpassung)
- Ersatzspieler-System

### 🗳️ Vote-System
- Admin-Command `/newcup datum1 datum2`
- Abstimmung mit Reactions (1️⃣ und 2️⃣)
- Automatisches Ende am 1. des nächsten Monats um 00:00 Uhr
- Ergebnisanzeige mit Stimmenzahl

### 👥 Spielerliste
- Separater Channel mit formatierter Liste
- Anzeige von Discord-Name, Valorant-Account und Ranks
- Unterscheidung zwischen regulären Spielern und Ersatzspielern
- Automatisches Update bei Anmeldungen

## Installation

1. **Dependencies installieren:**
```bash
pip install -r requirements.txt
```

2. **.env Datei konfigurieren:**
```
DISCORD-TOKEN=dein_discord_bot_token
API-KEY=dein_henrikdev_api_key
```

3. **Channel-IDs im Code eintragen:**
```python
ANNOUNCEMENT_CHANNEL_ID = 1234567890  # Channel für Hauptankündigung
VOTE_CHANNEL_ID = 1234567890          # Channel für Votes
PLAYER_LIST_CHANNEL_ID = 1234567890   # Channel für Spielerliste
```

4. **Bot starten:**
```bash
python main.py
```

## Befehle

### Admin-Befehle
- `/newcup datum1 datum2` - Erstellt eine neue Cup-Abstimmung
  - Beispiel: `/newcup 18.10.2025 25.10.2025`

## Funktionsweise

### Anmeldung
1. Spieler klickt auf "Anmelden"-Button
2. Modal öffnet sich für Valorant Name + Tag
3. Bot holt Rank-Informationen von der API
4. Spieler wird zur Liste hinzugefügt
5. Status wird bestimmt (regulär oder ersatz)

### Vote-System
1. Admin erstellt Vote mit `/newcup`
2. Vote-Nachricht mit 2 Optionen erscheint
3. Spieler stimmen mit Reactions ab
4. Am 1. des Monats um 00:00 Uhr:
   - Vote endet automatisch
   - Ergebnis wird angezeigt
   - Cup-Datum wird gesetzt
   - Spielerliste wird zurückgesetzt
   - Ankündigung wird aktualisiert

### Spielerzahl-System
- **10 Spieler:** Reguläres 2x5 Turnier
- **16 Spieler:** Erweitert auf 4x4 Teams
- **20 Spieler:** Erweitert auf 4x5 Teams
- **Mehr als Max:** Automatisch Ersatzspieler

## Datenstruktur

### cup_data.json
```json
{
  "current_cup": "2025-10-18T20:30:00",
  "current_vote": {
    "message_id": 123,
    "date1": "2025-10-18T20:30:00",
    "date2": "2025-10-25T20:30:00",
    "end_date": "2025-11-01T00:00:00"
  },
  "announcement_message_id": 123,
  "vote_message_id": 456,
  "player_list_message_id": 789,
  "winner_team": []
}
```

### players.json
```json
{
  "max_players": 10,
  "players": [
    {
      "discord_id": "123456789",
      "discord_name": "User#1234",
      "valorant_name": "RiotName",
      "valorant_tag": "EUW",
      "current_rank": "Gold 1",
      "highest_rank": "Platinum 3",
      "timestamp": "2025-10-04T12:00:00"
    }
  ]
}
```

## Embeds & Design

Alle Nachrichten nutzen Discord Embeds mit:
- ✅ Passende Farben (Gold für Cup, Grün für Erfolg, etc.)
- ✅ Übersichtliche Struktur mit Fields
- ✅ Icons und Emojis
- ✅ Thumbnails (Valorant Logo)
- ✅ Footer mit Zeitstempel

## API

Der Bot nutzt die **henrikdev Valorant API** für Rank-Informationen:
- Endpoint: `https://api.henrikdev.xyz/valorant/v2/mmr/eu/{name}/{tag}`
- Benötigt API-Key
- Liefert aktuellen und höchsten Rank

## Hinweise

- Bot benötigt `Administrator`-Rechte für Admin-Commands
- Buttons funktionieren persistent (bleiben nach Bot-Restart)
- Background-Task prüft jede Minute ob Vote endet
- Bei Problemen mit der API: Rate-Limits beachten

## Support

Bei Fragen oder Problemen erstelle ein Issue im Repository.
