import customtkinter as ctk
import requests
from datetime import datetime, timedelta
import re
from typing import List, Dict
import os
from tkinter import filedialog, messagebox, simpledialog
import calendar
import locale
import json

class CalendarEvent:
    def __init__(self, summary: str, start_date: datetime, end_date: datetime = None):
        self.summary = summary
        self.start_date = start_date
        self.end_date = end_date
        
    def get_date_string(self) -> str:
        """Formatiert das Datum für die Anzeige"""
        if self.end_date and self.end_date.date() != self.start_date.date():
            start_day = self.start_date.day
            end_day = self.end_date.day
            return f"{start_day}.-{end_day}."
        else:
            return f"{self.start_date.day}."

class NewsBoardGenerator:
    def __init__(self):
        self.events: List[CalendarEvent] = []
        self.selected_events: List[CalendarEvent] = []
        self.all_events: List[CalendarEvent] = []  # Alle geparsten Events
        self.current_limit = 20  # Aktuelles Anzeigelimit
        
        # Config-Dateipfad im User-Ordner
        self.config_dir = os.path.join(os.path.expanduser("~"), ".newsboarder")
        self.config_file = os.path.join(self.config_dir, "config.json")
        
        # Kalender-URL und Filter laden
        self.calendar_url = self.load_or_request_calendar_url()
        self.filter_words = self.load_filter_words()
        
        # Wenn keine URL (Benutzer hat abgebrochen), Programm beenden
        if not self.calendar_url:
            return
        
        # Deutsche Monatsnamen
        self.german_months = {
            1: "Januar", 2: "Februar", 3: "März", 4: "April",
            5: "Mai", 6: "Juni", 7: "Juli", 8: "August",
            9: "September", 10: "Oktober", 11: "November", 12: "Dezember"
        }
        
        # GUI Setup
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("News Board Generator")
        self.root.state('zoomed')  # Maximiert starten
        
        self.setup_gui()
        
        # Kalender automatisch beim Start laden
        self.root.after(100, self.load_calendar)
        
    def setup_gui(self):
        """Erstellt die GUI"""
        # Header
        header_frame = ctk.CTkFrame(self.root)
        header_frame.pack(fill="x", padx=20, pady=20)
        
        title_label = ctk.CTkLabel(header_frame, text="News Board Generator", 
                                 font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=20)
        
        # Button Frame für Header-Buttons
        header_button_frame = ctk.CTkFrame(header_frame)
        header_button_frame.pack(pady=10)
        
        # Mehr Events laden Button
        self.load_more_button = ctk.CTkButton(header_button_frame, text="Mehr Events laden", 
                                            command=self.load_more_events,
                                            state="disabled")
        self.load_more_button.pack(side="left", padx=5)
        
        # Filter verwalten Button
        filter_button = ctk.CTkButton(header_button_frame, text="Filter verwalten", 
                                     command=self.open_filter_manager)
        filter_button.pack(side="left", padx=5)
        
        # Main Content Frame
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left side - Events Liste
        left_frame = ctk.CTkFrame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Label mit Event-Zähler
        self.events_label = ctk.CTkLabel(left_frame, text="Verfügbare Termine:", 
                                  font=ctk.CTkFont(size=16, weight="bold"))
        self.events_label.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Suchleiste Frame
        search_frame = ctk.CTkFrame(left_frame)
        search_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        search_label = ctk.CTkLabel(search_frame, text="Suche:", width=60)
        search_label.pack(side="left", padx=(0, 10))
        
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.on_search_changed())
        
        self.search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var, 
                                        placeholder_text="Events durchsuchen...")
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        clear_search_btn = ctk.CTkButton(search_frame, text="✕", width=30,
                                        command=self.clear_search)
        clear_search_btn.pack(side="left")
        
        # Scrollable Frame für Events
        self.events_scroll = ctk.CTkScrollableFrame(left_frame, height=400)
        self.events_scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Right side - Selected Events with Edit Table
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        selected_label = ctk.CTkLabel(right_frame, text="Ausgewählte Termine (max. 4):", 
                                    font=ctk.CTkFont(size=16, weight="bold"))
        selected_label.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Bearbeitungstabelle
        self.create_edit_table(right_frame)
        
        # Buttons
        button_frame = ctk.CTkFrame(self.root)
        button_frame.pack(fill="x", padx=20, pady=20)
        
        copy_button = ctk.CTkButton(button_frame, text="In Zwischenablage kopieren", 
                                   command=self.copy_to_clipboard)
        copy_button.pack(side="left", padx=10)
        
        clear_button = ctk.CTkButton(button_frame, text="Auswahl zurücksetzen", 
                                   command=self.clear_selection)
        clear_button.pack(side="left", padx=10)
        
        # Config löschen Button
        reset_button = ctk.CTkButton(button_frame, text="Kalender-URL zurücksetzen & Beenden", 
                                    command=self.reset_config_and_exit,
                                    fg_color="red", hover_color="darkred")
        reset_button.pack(side="right", padx=10)
    
    def create_edit_table(self, parent):
        """Erstellt die Bearbeitungstabelle für ausgewählte Events"""
        # Header
        header_frame = ctk.CTkFrame(parent)
        header_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(header_frame, text="Nr.", width=40, 
                    font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Datum", width=100, 
                    font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Event", width=300, 
                    font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(header_frame, text="Aktionen", width=120, 
                    font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        
        # Scrollable Table Frame
        self.table_frame = ctk.CTkScrollableFrame(parent, height=350)
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Liste für Entry-Widgets
        self.date_entries = []
        self.event_entries = []
        
    def update_edit_table(self):
        """Aktualisiert die Bearbeitungstabelle"""
        # Lösche alte Einträge
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        
        self.date_entries.clear()
        self.event_entries.clear()
        
        # Erstelle Einträge für ausgewählte Events
        for i, event in enumerate(self.selected_events):
            row_frame = ctk.CTkFrame(self.table_frame)
            row_frame.pack(fill="x", pady=2)
            
            # Nummer
            ctk.CTkLabel(row_frame, text=f"{i+1}.", width=40).pack(side="left", padx=5)
            
            # Datum Entry
            date_entry = ctk.CTkEntry(row_frame, width=100)
            date_entry.insert(0, event.get_date_string())
            date_entry.pack(side="left", padx=5)
            self.date_entries.append(date_entry)
            
            # Event Entry
            event_entry = ctk.CTkEntry(row_frame, width=300)
            event_entry.insert(0, event.summary)
            event_entry.pack(side="left", padx=5)
            self.event_entries.append(event_entry)
            
            # Entfernen Button
            remove_btn = ctk.CTkButton(row_frame, text="Entfernen", width=80,
                                     command=lambda idx=i: self.remove_selected_event(idx))
            remove_btn.pack(side="left", padx=5)
            
            # Nach oben/unten Buttons
            if i > 0:
                up_btn = ctk.CTkButton(row_frame, text="↑", width=30,
                                     command=lambda idx=i: self.move_event_up(idx))
                up_btn.pack(side="left", padx=2)
            
            if i < len(self.selected_events) - 1:
                down_btn = ctk.CTkButton(row_frame, text="↓", width=30,
                                       command=lambda idx=i: self.move_event_down(idx))
                down_btn.pack(side="left", padx=2)
        
        # Füge leere Zeilen hinzu falls weniger als 4 Events
        for i in range(len(self.selected_events), 4):
            row_frame = ctk.CTkFrame(self.table_frame)
            row_frame.pack(fill="x", pady=2)
            
            ctk.CTkLabel(row_frame, text=f"{i+1}.", width=40).pack(side="left", padx=5)
            
            date_entry = ctk.CTkEntry(row_frame, width=100, placeholder_text="Datum")
            date_entry.pack(side="left", padx=5)
            self.date_entries.append(date_entry)
            
            event_entry = ctk.CTkEntry(row_frame, width=300, placeholder_text="Event-Name")
            event_entry.pack(side="left", padx=5)
            self.event_entries.append(event_entry)
            
            ctk.CTkLabel(row_frame, text="", width=120).pack(side="left", padx=5)
    
    def remove_selected_event(self, index):
        """Entfernt ein ausgewähltes Event"""
        if 0 <= index < len(self.selected_events):
            self.selected_events.pop(index)
            self.update_edit_table()
            self.display_events()  # Refresh verfügbare Events
    
    def move_event_up(self, index):
        """Bewegt Event nach oben"""
        if index > 0:
            self.selected_events[index], self.selected_events[index-1] = \
                self.selected_events[index-1], self.selected_events[index]
            self.update_edit_table()
    
    def move_event_down(self, index):
        """Bewegt Event nach unten"""
        if index < len(self.selected_events) - 1:
            self.selected_events[index], self.selected_events[index+1] = \
                self.selected_events[index+1], self.selected_events[index]
            self.update_edit_table()

    def parse_ical(self, ical_content: str) -> List[CalendarEvent]:
        """Parst iCal Content und extrahiert Events"""
        events = []
        current_event = {}
        all_events_debug = []  # Für Debugging der ersten 10 Events
        
        # Debug: Zeige ersten Teil des iCal Contents
        print(f"iCal Content (erste 500 Zeichen):\n{ical_content[:500]}")
        print(f"Gesamtlänge: {len(ical_content)} Zeichen")
        
        lines = ical_content.replace('\r\n', '\n').replace('\r', '\n').split('\n')
        print(f"Anzahl Zeilen: {len(lines)}")
        
        event_count = 0
        for line in lines:
            line = line.strip()
            
            if line == 'BEGIN:VEVENT':
                current_event = {}
                event_count += 1
                
            elif line == 'END:VEVENT':
                # Speichere alle Event-Daten für Debug (erste 10)
                if len(all_events_debug) < 10:
                    all_events_debug.append({
                        'event_num': event_count,
                        'summary': current_event.get('SUMMARY', 'FEHLT'),
                        'dtstart': current_event.get('DTSTART', 'FEHLT'),
                        'dtend': current_event.get('DTEND', 'FEHLT'),
                        'description': current_event.get('DESCRIPTION', 'FEHLT'),
                        'location': current_event.get('LOCATION', 'FEHLT'),
                        'all_keys': list(current_event.keys())
                    })
                
                if 'SUMMARY' in current_event and 'DTSTART' in current_event:
                    try:
                        # Parse Datum - erweiterte Formate
                        start_str = current_event['DTSTART']
                        
                        # Verschiedene Datumsformate probieren
                        start_date = None
                        date_formats = [
                            '%Y%m%dT%H%M%S',
                            '%Y%m%dT%H%M%SZ',
                            '%Y%m%d',
                            '%Y-%m-%d',
                            '%Y-%m-%dT%H:%M:%S',
                            '%Y%m%dT%H%M%S%z'
                        ]
                        
                        for fmt in date_formats:
                            try:
                                start_date = datetime.strptime(start_str, fmt)
                                break
                            except:
                                continue
                        
                        if start_date is None:
                            continue
                        
                        # End-Datum parsen
                        end_date = None
                        if 'DTEND' in current_event:
                            end_str = current_event['DTEND']
                            
                            for fmt in date_formats:
                                try:
                                    end_date = datetime.strptime(end_str, fmt)
                                    break
                                except:
                                    continue
                        
                        # Prüfe ob Event in der Zukunft liegt
                        today = datetime.now().date()
                        event_date = start_date.date()
                        
                        if event_date >= today:
                            event = CalendarEvent(current_event['SUMMARY'], start_date, end_date)
                            events.append(event)
                            
                    except Exception as e:
                        continue
                        
            elif ':' in line:
                try:
                    # Erweiterte Feldnamen-Parsing für Parameter wie DTSTART;TZID=Europe/Berlin
                    if ';' in line and ':' in line:
                        # Format: FELDNAME;PARAMETER:WERT
                        field_part, value = line.split(':', 1)
                        field_name = field_part.split(';')[0]  # Nur der Hauptfeldname
                        current_event[field_name] = value
                    else:
                        # Standard Format: FELDNAME:WERT
                        key, value = line.split(':', 1)
                        current_event[key] = value
                except:
                    continue
        
        # Debug-Ausgabe für die ersten 10 Events
        print("\n" + "="*80)
        print("DETAILLIERTE DEBUG-AUSGABE DER ERSTEN 10 EVENTS:")
        print("="*80)
        
        for debug_event in all_events_debug:
            print(f"\nEvent #{debug_event['event_num']}:")
            print(f"  SUMMARY: {debug_event['summary']}")
            print(f"  DTSTART: {debug_event['dtstart']}")
            print(f"  DTEND: {debug_event['dtend']}")
            print(f"  DESCRIPTION: {debug_event['description'][:100] if debug_event['description'] != 'FEHLT' else 'FEHLT'}...")
            print(f"  LOCATION: {debug_event['location']}")
            print(f"  Verfügbare Felder: {debug_event['all_keys']}")
            
            # Prüfe Vollständigkeit
            has_summary = debug_event['summary'] != 'FEHLT'
            has_dtstart = debug_event['dtstart'] != 'FEHLT'
            
            if has_summary and has_dtstart:
                print(f"  ✅ EVENT VOLLSTÄNDIG")
                
                start_str = debug_event['dtstart']
                print(f"  📅 DTSTART Wert: {start_str}")
                
                # Test Datumsparsing
                date_formats = [
                    '%Y%m%dT%H%M%S', '%Y%m%dT%H%M%SZ', '%Y%m%d',
                    '%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y%m%dT%H%M%S%z'
                ]
                
                parsed_date = None
                for fmt in date_formats:
                    try:
                        parsed_date = datetime.strptime(start_str, fmt)
                        print(f"  ✅ Datum erfolgreich geparst mit Format '{fmt}': {parsed_date}")
                        break
                    except Exception as e:
                        print(f"  ❌ Format '{fmt}' fehlgeschlagen: {e}")
                
                if parsed_date:
                    today = datetime.now().date()
                    event_date = parsed_date.date()
                    is_future = event_date >= today
                    print(f"  📅 Event-Datum: {event_date}")
                    print(f"  📅 Heute: {today}")
                    print(f"  {'✅' if is_future else '❌'} Event in der Zukunft: {is_future}")
                else:
                    print(f"  ❌ DATUM KONNTE NICHT GEPARST WERDEN")
                    
            else:
                print(f"  ❌ EVENT UNVOLLSTÄNDIG:")
                print(f"     SUMMARY vorhanden: {has_summary}")
                print(f"     DTSTART vorhanden: {has_dtstart}")
        
        print(f"\n{'='*80}")
        print(f"ZUSAMMENFASSUNG:")
        print(f"Insgesamt {event_count} Events im iCal gefunden")
        print(f"Davon {len(events)} gültige Events nach Filterung")
        print(f"{'='*80}\n")
        
        # Sortiere nach Datum
        events.sort(key=lambda x: x.start_date)
        
        # Filtere Events basierend auf Filterwörtern
        events = self.apply_filters(events)
        
        return events  # Gebe alle gefilterten Events zurück
    
    def load_calendar(self):
        """Lädt Kalender von der URL"""
        try:
            print(f"Lade Kalender von: {self.calendar_url}")
            
            response = requests.get(self.calendar_url, timeout=10)
            print(f"HTTP Status: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type', 'unbekannt')}")
            
            response.raise_for_status()
            
            # Debug: Speichere rohen Content in Datei
            debug_file = os.path.join(os.path.dirname(__file__), "debug_ical.txt")
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"Roher iCal Content gespeichert in: {debug_file}")
            
            self.all_events = self.parse_ical(response.text)
            self.current_limit = 20  # Setze Limit zurück
            self.events = self.all_events[:self.current_limit]  # Zeige erste 20
            self.update_events_label()
            self.display_events()
            
            # Aktiviere "Mehr laden" Button wenn mehr Events verfügbar
            if len(self.all_events) > self.current_limit:
                self.load_more_button.configure(state="normal")
            else:
                self.load_more_button.configure(state="disabled")
            
            messagebox.showinfo("Erfolg", f"{len(self.events)} von {len(self.all_events)} Terminen geladen!")
            
        except Exception as e:
            print(f"Fehler beim Laden: {e}")
            messagebox.showerror("Fehler", f"Kalender konnte nicht geladen werden:\n{str(e)}")
    
    def apply_filters(self, events: List[CalendarEvent]) -> List[CalendarEvent]:
        """Filtert Events basierend auf den Filterwörtern"""
        if not self.filter_words:
            return events
        
        filtered_events = []
        for event in events:
            # Prüfe ob ein Filterwort im Event-Namen vorkommt (case-insensitive)
            summary_lower = event.summary.lower()
            contains_filter = any(word.lower() in summary_lower for word in self.filter_words)
            
            # Event nur hinzufügen wenn KEIN Filterwort gefunden wurde
            if not contains_filter:
                filtered_events.append(event)
        
        print(f"Filter angewendet: {len(events)} Events -> {len(filtered_events)} Events nach Filterung")
        print(f"Aktive Filter: {', '.join(self.filter_words) if self.filter_words else 'Keine'}")
        
        return filtered_events
    
    def load_more_events(self):
        """Lädt weitere Events (jeweils 20 mehr)"""
        if len(self.all_events) > self.current_limit:
            # Erhöhe Limit um 20
            self.current_limit += 20
            
            # Aktualisiere angezeigte Events
            self.events = self.all_events[:self.current_limit]
            self.update_events_label()
            self.display_events()
            
            # Deaktiviere Button wenn alle Events geladen
            if len(self.all_events) <= self.current_limit:
                self.load_more_button.configure(state="disabled")
                messagebox.showinfo("Info", f"Alle {len(self.all_events)} Termine wurden geladen!")
            else:
                messagebox.showinfo("Erfolg", f"{len(self.events)} von {len(self.all_events)} Terminen geladen!")
    
    def update_events_label(self):
        """Aktualisiert das Label mit der Event-Anzahl"""
        total = len(self.all_events)
        shown = len(self.events)
        
        if total > shown:
            self.events_label.configure(text=f"Verfügbare Termine ({shown} von {total} geladen):")
        else:
            self.events_label.configure(text=f"Verfügbare Termine ({total} Termine):")
    
    def display_events(self):
        """Zeigt Events in der GUI an (nur nicht ausgewählte)"""
        # Lösche alte Events
        for widget in self.events_scroll.winfo_children():
            widget.destroy()
            
        # Filtere ausgewählte Events heraus
        available_events = [event for event in self.events if event not in self.selected_events]
        
        # Filtere basierend auf Suchtext
        search_text = self.search_var.get().strip().lower() if hasattr(self, 'search_var') else ""
        if search_text:
            available_events = [event for event in available_events 
                              if search_text in event.summary.lower()]
            
        for i, event in enumerate(available_events):
            event_frame = ctk.CTkFrame(self.events_scroll)
            event_frame.pack(fill="x", pady=5)
            
            # Event Info
            date_str = event.get_date_string()
            month_name = self.german_months.get(event.start_date.month, "Unbekannt")
            
            info_text = f"{date_str} {month_name} - {event.summary}"
            
            # Nur Auswählen-Button anzeigen wenn weniger als 4 Events ausgewählt
            if len(self.selected_events) < 4:
                event_button = ctk.CTkButton(event_frame, text="Auswählen", 
                                           command=lambda e=event: self.select_event(e))
                event_button.pack(side="right", padx=10, pady=5)
            
            event_label = ctk.CTkLabel(event_frame, text=info_text, anchor="w")
            event_label.pack(side="left", fill="x", expand=True, padx=10, pady=5)
    
    def on_search_changed(self):
        """Wird aufgerufen wenn sich der Suchtext ändert"""
        self.display_events()
    
    def clear_search(self):
        """Löscht den Suchtext"""
        self.search_var.set("")
    
    def select_event(self, event: CalendarEvent):
        """Wählt ein Event aus"""
        if len(self.selected_events) < 4 and event not in self.selected_events:
            self.selected_events.append(event)
            self.update_edit_table()
            self.display_events()  # Refresh um ausgewählte Events zu verstecken
    
    def clear_selection(self):
        """Setzt die Auswahl zurück"""
        self.selected_events.clear()
        self.update_edit_table()
        self.display_events()
    
    def copy_to_clipboard(self):
        """Kopiert das News Board in die Zwischenablage"""
        # Hole aktuelle Werte aus den Entry-Feldern
        current_dates = [entry.get().strip() for entry in self.date_entries]
        current_events = [entry.get().strip() for entry in self.event_entries]
        
        # Prüfe ob mindestens ein Event eingetragen ist
        if not any(current_events):
            messagebox.showwarning("Warnung", "Bitte tragen Sie mindestens ein Event ein!")
            return
            
        try:
            # Template laden
            template_path = os.path.join(os.path.dirname(__file__), "template.setting")
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Monat für Überschrift bestimmen (vom ersten Event mit Datum)
            month_name = "Aktueller Monat"
            for i, event in enumerate(self.selected_events):
                if i < len(current_events) and current_events[i]:
                    month_name = self.german_months.get(event.start_date.month, "Aktueller Monat")
                    break
            
            # Template ausfüllen mit aktuellen Werten
            modified_content = self.fill_template_with_current_values(
                template_content, month_name, current_dates, current_events)
            
            # In Zwischenablage kopieren
            self.root.clipboard_clear()
            self.root.clipboard_append(modified_content)
            self.root.update()  # Wichtig für die Zwischenablage
            
            messagebox.showinfo("Erfolg", "News Board wurde in die Zwischenablage kopiert!")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Kopieren:\n{str(e)}")
    
    def fill_template_with_current_values(self, template: str, month_name: str, 
                                        dates: List[str], events: List[str]) -> str:
        """Füllt das Template mit den aktuellen Werten aus der Tabelle"""
        # Überschrift
        template = template.replace('Termine im <Monat>', f'Termine im {month_name}')
        
        # Events einsetzen basierend auf Tabellenwerten
        template_replacements = [
            ('StyledText = Input { Value = "01.-02.", }', 'StyledText = Input { Value = "Beispiel Feiertag [schulfrei]", }'),
            ('StyledText = Input { Value = "10.", }', 'StyledText = Input { Value = "Beispiel Konzert", }'),
            ('StyledText = Input { Value = "17.-20.", }', 'StyledText = Input { Value = "Beispiel Sporttag", }'),
            ('StyledText = Input { Value = "30.", }', 'StyledText = Input { Value = "Beispiel Irgendwas [schulfrei]", }')
        ]
        
        for i in range(4):
            date_str = dates[i] if i < len(dates) and dates[i] else ""
            event_str = events[i] if i < len(events) and events[i] else ""
            
            # Ersetze Template-Werte
            if i < len(template_replacements):
                old_date, old_event = template_replacements[i]
                new_date = f'StyledText = Input {{ Value = "{date_str}", }}'
                new_event = f'StyledText = Input {{ Value = "{event_str}", }}'
                
                template = template.replace(old_date, new_date)
                template = template.replace(old_event, new_event)
        
        return template

    def load_or_request_calendar_url(self) -> str:
        """Lädt die Kalender-URL aus der Config oder fragt den Benutzer"""
        # Prüfe ob Config existiert
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get('calendar_url', '')
            except Exception as e:
                print(f"Fehler beim Laden der Config: {e}")
        
        # Config existiert nicht oder ist fehlerhaft - Benutzer fragen
        return self.request_calendar_url()
    
    def load_filter_words(self) -> List[str]:
        """Lädt die Filterwörter aus der Config"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get('filter_words', [])
            except Exception as e:
                print(f"Fehler beim Laden der Filter: {e}")
        return []
    
    def save_filter_words(self):
        """Speichert die Filterwörter in der Config"""
        try:
            # Lade existierende Config
            config = {}
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            # Aktualisiere Filter
            config['filter_words'] = self.filter_words
            
            # Speichere Config
            os.makedirs(self.config_dir, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            print(f"Filter gespeichert: {self.filter_words}")
        except Exception as e:
            print(f"Fehler beim Speichern der Filter: {e}")
            messagebox.showerror("Fehler", f"Filter konnten nicht gespeichert werden:\n{str(e)}")
    
    def open_filter_manager(self):
        """Öffnet ein Fenster zum Verwalten der Filterwörter"""
        # Erstelle neues Fenster
        filter_window = ctk.CTkToplevel(self.root)
        filter_window.title("Filter verwalten")
        filter_window.geometry("500x400")
        filter_window.transient(self.root)
        filter_window.grab_set()
        
        # Titel
        title_label = ctk.CTkLabel(filter_window, text="Event-Filter verwalten", 
                                   font=ctk.CTkFont(size=18, weight="bold"))
        title_label.pack(pady=20)
        
        # Beschreibung
        desc_label = ctk.CTkLabel(filter_window, 
                                 text="Events, die eines dieser Wörter enthalten, werden ausgeblendet:",
                                 wraplength=450)
        desc_label.pack(pady=10)
        
        # Frame für Filter-Liste
        list_frame = ctk.CTkFrame(filter_window)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Scrollable Frame für Filter
        filter_scroll = ctk.CTkScrollableFrame(list_frame, height=200)
        filter_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        def refresh_filter_list():
            """Aktualisiert die Anzeige der Filterwörter"""
            for widget in filter_scroll.winfo_children():
                widget.destroy()
            
            if not self.filter_words:
                empty_label = ctk.CTkLabel(filter_scroll, text="Keine Filter aktiv", 
                                          text_color="gray")
                empty_label.pack(pady=20)
            else:
                for i, word in enumerate(self.filter_words):
                    filter_frame = ctk.CTkFrame(filter_scroll)
                    filter_frame.pack(fill="x", pady=2)
                    
                    word_label = ctk.CTkLabel(filter_frame, text=word, anchor="w")
                    word_label.pack(side="left", fill="x", expand=True, padx=10, pady=5)
                    
                    remove_btn = ctk.CTkButton(filter_frame, text="Entfernen", width=80,
                                             command=lambda w=word: remove_filter(w))
                    remove_btn.pack(side="right", padx=5, pady=5)
        
        def add_filter():
            """Fügt ein neues Filterwort hinzu"""
            word = simpledialog.askstring("Filter hinzufügen", 
                                         "Geben Sie ein Wort ein, das gefiltert werden soll:",
                                         parent=filter_window)
            if word and word.strip():
                word = word.strip()
                if word not in self.filter_words:
                    self.filter_words.append(word)
                    self.save_filter_words()
                    refresh_filter_list()
                    messagebox.showinfo("Erfolg", f"Filter '{word}' hinzugefügt!", parent=filter_window)
                else:
                    messagebox.showwarning("Warnung", f"Filter '{word}' existiert bereits!", parent=filter_window)
        
        def remove_filter(word: str):
            """Entfernt ein Filterwort"""
            if word in self.filter_words:
                self.filter_words.remove(word)
                self.save_filter_words()
                refresh_filter_list()
        
        def close_and_reload():
            """Schließt das Fenster und lädt den Kalender neu"""
            filter_window.destroy()
            # Kalender neu laden um Filter anzuwenden
            self.load_calendar()
        
        # Initiale Anzeige
        refresh_filter_list()
        
        # Button Frame
        button_frame = ctk.CTkFrame(filter_window)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        add_button = ctk.CTkButton(button_frame, text="Filter hinzufügen", 
                                  command=add_filter)
        add_button.pack(side="left", padx=5)
        
        close_button = ctk.CTkButton(button_frame, text="Schließen & Neu laden", 
                                    command=close_and_reload)
        close_button.pack(side="right", padx=5)
    
    def request_calendar_url(self) -> str:
        """Fragt den Benutzer nach der Kalender-URL"""
        # Temporäres Fenster für die Abfrage
        root = ctk.CTk()
        root.withdraw()  # Verstecke Hauptfenster
        
        url = simpledialog.askstring(
            "Kalender-URL",
            "Bitte geben Sie die iCal-URL Ihres Kalenders ein:",
            parent=root
        )
        
        root.destroy()
        
        if url and url.strip():
            url = url.strip()
            # Speichere URL in Config
            self.save_calendar_url(url)
            return url
        
        return ""
    
    def save_calendar_url(self, url: str):
        """Speichert die Kalender-URL in der Config-Datei"""
        try:
            # Erstelle Config-Verzeichnis falls nicht vorhanden
            os.makedirs(self.config_dir, exist_ok=True)
            
            # Lade existierende Config (um Filter zu behalten)
            config = {}
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            # Aktualisiere URL
            config['calendar_url'] = url
            
            # Speichere Config
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            print(f"Kalender-URL gespeichert in: {self.config_file}")
        except Exception as e:
            print(f"Fehler beim Speichern der Config: {e}")
            messagebox.showerror("Fehler", f"Kalender-URL konnte nicht gespeichert werden:\n{str(e)}")
    
    def reset_config_and_exit(self):
        """Löscht die Config-Datei und beendet das Programm"""
        result = messagebox.askyesno(
            "Bestätigung",
            "Möchten Sie wirklich die Kalender-URL zurücksetzen?\n\n"
            "Die gespeicherte URL wird gelöscht und das Programm beendet.\n"
            "Beim nächsten Start werden Sie nach einer neuen URL gefragt."
        )
        
        if result:
            try:
                if os.path.exists(self.config_file):
                    os.remove(self.config_file)
                    print(f"Config-Datei gelöscht: {self.config_file}")
                
                messagebox.showinfo("Erfolg", "Kalender-URL wurde zurückgesetzt.\nDas Programm wird jetzt beendet.")
                self.root.quit()
                self.root.destroy()
            except Exception as e:
                messagebox.showerror("Fehler", f"Config konnte nicht gelöscht werden:\n{str(e)}")
    
    def run(self):
        """Startet die Anwendung"""
        if hasattr(self, 'root'):
            self.root.mainloop()

if __name__ == "__main__":
    app = NewsBoardGenerator()
    if hasattr(app, 'root'):
        app.run()
