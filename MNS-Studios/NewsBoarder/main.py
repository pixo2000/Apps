import customtkinter as ctk
import requests
from datetime import datetime, timedelta
import re
from typing import List, Dict
import os
from tkinter import filedialog, messagebox
import calendar
import locale

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
        self.calendar_url = "https://start.schulportal.hessen.de/kalender.php?a=ical&i=5214&export=ical&t=47398d6bf42ddcd5ef343c4ea5b11d43b6e8da0521c802b72a5c5a9d789ec66050290985756de16055299d2b38e37ea0d38d1fe7ffdda667287a46110829c439"
        
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
        self.root.geometry("1200x800")
        
        self.setup_gui()
        
    def setup_gui(self):
        """Erstellt die GUI"""
        # Header
        header_frame = ctk.CTkFrame(self.root)
        header_frame.pack(fill="x", padx=20, pady=20)
        
        title_label = ctk.CTkLabel(header_frame, text="News Board Generator", 
                                 font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=20)
        
        # Kalender laden Button
        load_button = ctk.CTkButton(header_frame, text="Kalender laden", 
                                  command=self.load_calendar)
        load_button.pack(pady=10)
        
        # Main Content Frame
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left side - Events Liste
        left_frame = ctk.CTkFrame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        events_label = ctk.CTkLabel(left_frame, text="Verfügbare Termine:", 
                                  font=ctk.CTkFont(size=16, weight="bold"))
        events_label.pack(anchor="w", padx=20, pady=(20, 10))
        
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
        
        generate_button = ctk.CTkButton(button_frame, text="News Board generieren", 
                                      command=self.generate_newsboard)
        generate_button.pack(side="left", padx=10)
        
        clear_button = ctk.CTkButton(button_frame, text="Auswahl zurücksetzen", 
                                   command=self.clear_selection)
        clear_button.pack(side="left", padx=10)
        
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
        return events[:20]  # Begrenzt auf 20 Events
    
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
            
            self.events = self.parse_ical(response.text)
            self.display_events()
            
            messagebox.showinfo("Erfolg", f"{len(self.events)} Termine geladen!")
            
        except Exception as e:
            print(f"Fehler beim Laden: {e}")
            messagebox.showerror("Fehler", f"Kalender konnte nicht geladen werden:\n{str(e)}")
    
    def display_events(self):
        """Zeigt Events in der GUI an (nur nicht ausgewählte)"""
        # Lösche alte Events
        for widget in self.events_scroll.winfo_children():
            widget.destroy()
            
        # Filtere ausgewählte Events heraus
        available_events = [event for event in self.events if event not in self.selected_events]
            
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
    
    def generate_newsboard(self):
        """Generiert das News Board"""
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
            
            # Speichern
            output_path = filedialog.asksaveasfilename(
                defaultextension=".setting",
                filetypes=[("DaVinci Resolve Settings", "*.setting"), ("All files", "*.*")],
                title="News Board speichern"
            )
            
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                
                messagebox.showinfo("Erfolg", f"News Board wurde gespeichert:\n{output_path}")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Generieren:\n{str(e)}")
    
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
            
            # Kürze Event-Name falls zu lang
            if len(event_str) > 30:
                event_str = event_str[:27] + "..."
            
            # Ersetze Template-Werte
            if i < len(template_replacements):
                old_date, old_event = template_replacements[i]
                new_date = f'StyledText = Input {{ Value = "{date_str}", }}'
                new_event = f'StyledText = Input {{ Value = "{event_str}", }}'
                
                template = template.replace(old_date, new_date)
                template = template.replace(old_event, new_event)
        
        return template

    def run(self):
        """Startet die Anwendung"""
        self.root.mainloop()

if __name__ == "__main__":
    app = NewsBoardGenerator()
    app.run()
