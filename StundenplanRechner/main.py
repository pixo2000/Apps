#!/usr/bin/env python3
"""
Lanis Schulportal Vertretungsplan Analyzer
==========================================

This application connects to the Lanis Schulportal, fetches the Vertretungsplan (substitution plan),
and calculates the schedule for every class with room and teacher information.

Features:
- Secure credential storage with .env file
- Web scraping of Lanis Schulportal
- Vertretungsplan parsing and analysis
- Schedule calculation for all classes
- GUI interface for easy use
- Export functionality to CSV/Excel

Author: pixo2000
Date: August 2025
"""

import os
import json
import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import time
import re

# Load environment variables
load_dotenv()

class LanisPortalScraper:
    """Handles all interactions with the Lanis Schulportal"""
    
    def __init__(self):
        self.session = requests.Session()
        self.driver = None
        self.is_logged_in = False
        self.school_id = os.getenv('LANIS_SCHOOL_ID', '')
        
    def setup_driver(self):
        """Setup Selenium WebDriver for JavaScript-heavy pages"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in background
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        return self.driver
    
    def login(self, username, password, school_id=None):
        """Login to Lanis Schulportal"""
        try:
            if not self.driver:
                self.setup_driver()
            
            # Navigate to login page
            login_url = f"https://connect.schulportal.hessen.de"
            self.driver.get(login_url)
            
            # Wait for page to load
            wait = WebDriverWait(self.driver, 10)
            
            # Find and fill school ID field
            if school_id:
                school_field = wait.until(EC.presence_of_element_located((By.NAME, "schulnummer")))
                school_field.clear()
                school_field.send_keys(school_id)
            
            # Find and fill username field
            username_field = wait.until(EC.presence_of_element_located((By.NAME, "user")))
            username_field.clear()
            username_field.send_keys(username)
            
            # Find and fill password field
            password_field = self.driver.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys(password)
            
            # Submit login form
            login_button = self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
            login_button.click()
            
            # Wait for redirect after login
            time.sleep(3)
            
            # Check if login was successful
            current_url = self.driver.current_url
            if "login" not in current_url.lower() and "anmeldung" not in current_url.lower():
                self.is_logged_in = True
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Login error: {str(e)}")
            return False
    
    def get_vertretungsplan(self):
        """Fetch the Vertretungsplan data"""
        if not self.is_logged_in:
            raise Exception("Not logged in to Lanis Portal")
        
        try:
            # Navigate to Vertretungsplan
            vertretungsplan_url = "https://connect.schulportal.hessen.de/vertretungsplan.php"
            self.driver.get(vertretungsplan_url)
            
            # Wait for page to load
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            
            # Get page source and parse with BeautifulSoup
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Find all tables (usually one for each day)
            tables = soup.find_all('table', class_=['vertretung', 'mon_list'])
            
            vertretungsplan_data = []
            
            for table in tables:
                # Extract date information
                date_header = table.find_previous(['h3', 'h2', 'div'], string=re.compile(r'\d{2}\.\d{2}\.\d{4}'))
                date_str = ""
                if date_header:
                    date_match = re.search(r'(\d{2}\.\d{2}\.\d{4})', date_header.get_text())
                    if date_match:
                        date_str = date_match.group(1)
                
                # Parse table rows
                rows = table.find_all('tr')
                headers = []
                
                # Get headers
                if rows:
                    header_row = rows[0]
                    headers = [th.get_text().strip() for th in header_row.find_all(['th', 'td'])]
                
                # Process data rows
                for row in rows[1:]:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 4:  # Minimum expected columns
                        row_data = {}
                        for i, cell in enumerate(cells):
                            if i < len(headers):
                                row_data[headers[i]] = cell.get_text().strip()
                        
                        row_data['date'] = date_str
                        vertretungsplan_data.append(row_data)
            
            return vertretungsplan_data
            
        except Exception as e:
            print(f"Error fetching Vertretungsplan: {str(e)}")
            return []
    
    def get_regular_schedule(self):
        """Fetch regular class schedule if available"""
        try:
            # Navigate to schedule page
            schedule_url = "https://connect.schulportal.hessen.de/stundenplan.php"
            self.driver.get(schedule_url)
            
            # Wait for page to load
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            
            # Get page source and parse
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Parse schedule tables
            schedule_data = {}
            tables = soup.find_all('table')
            
            for table in tables:
                # Extract class information and schedule
                class_header = table.find_previous(['h3', 'h2'])
                if class_header:
                    class_name = class_header.get_text().strip()
                    
                    rows = table.find_all('tr')
                    if rows:
                        headers = [th.get_text().strip() for th in rows[0].find_all(['th', 'td'])]
                        
                        class_schedule = []
                        for row in rows[1:]:
                            cells = row.find_all(['td', 'th'])
                            if cells:
                                row_data = {}
                                for i, cell in enumerate(cells):
                                    if i < len(headers):
                                        row_data[headers[i]] = cell.get_text().strip()
                                class_schedule.append(row_data)
                        
                        schedule_data[class_name] = class_schedule
            
            return schedule_data
            
        except Exception as e:
            print(f"Error fetching regular schedule: {str(e)}")
            return {}
    
    def close(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()

class ScheduleCalculator:
    """Calculates and processes schedule data"""
    
    def __init__(self):
        self.regular_schedule = {}
        self.vertretungsplan = []
        self.calculated_schedules = {}
    
    def load_data(self, regular_schedule, vertretungsplan):
        """Load schedule data for processing"""
        self.regular_schedule = regular_schedule
        self.vertretungsplan = vertretungsplan
    
    def calculate_daily_schedules(self):
        """Calculate daily schedules for all classes incorporating substitutions"""
        self.calculated_schedules = {}
        
        # Group Vertretungsplan by date
        substitutions_by_date = {}
        for entry in self.vertretungsplan:
            date = entry.get('date', '')
            if date not in substitutions_by_date:
                substitutions_by_date[date] = []
            substitutions_by_date[date].append(entry)
        
        # Calculate schedules for each class and date
        for class_name, regular_lessons in self.regular_schedule.items():
            if class_name not in self.calculated_schedules:
                self.calculated_schedules[class_name] = {}
            
            # Calculate for each date that has substitutions
            for date, substitutions in substitutions_by_date.items():
                daily_schedule = []
                
                # Start with regular schedule
                for lesson in regular_lessons:
                    modified_lesson = lesson.copy()
                    
                    # Check for substitutions affecting this lesson
                    for sub in substitutions:
                        if self._lesson_matches_substitution(lesson, sub, class_name):
                            modified_lesson = self._apply_substitution(modified_lesson, sub)
                    
                    daily_schedule.append(modified_lesson)
                
                # Add new lessons from substitutions
                for sub in substitutions:
                    if self._is_additional_lesson(sub, class_name, regular_lessons):
                        new_lesson = self._create_lesson_from_substitution(sub)
                        daily_schedule.append(new_lesson)
                
                self.calculated_schedules[class_name][date] = daily_schedule
        
        return self.calculated_schedules
    
    def _lesson_matches_substitution(self, lesson, substitution, class_name):
        """Check if a lesson matches a substitution entry"""
        # This is a simplified matching logic - you may need to adjust based on actual data structure
        lesson_time = lesson.get('Zeit', lesson.get('Stunde', ''))
        sub_time = substitution.get('Stunde', substitution.get('Zeit', ''))
        
        lesson_class = lesson.get('Klasse', class_name)
        sub_class = substitution.get('Klasse', substitution.get('Klassen', ''))
        
        return lesson_time == sub_time and (lesson_class == sub_class or class_name in sub_class)
    
    def _apply_substitution(self, lesson, substitution):
        """Apply substitution to a lesson"""
        modified_lesson = lesson.copy()
        
        # Apply changes from substitution
        if 'Lehrer' in substitution and substitution['Lehrer']:
            modified_lesson['Lehrer'] = substitution['Lehrer']
        if 'Raum' in substitution and substitution['Raum']:
            modified_lesson['Raum'] = substitution['Raum']
        if 'Fach' in substitution and substitution['Fach']:
            modified_lesson['Fach'] = substitution['Fach']
        
        # Add substitution info
        modified_lesson['substitution_info'] = substitution.get('Bemerkung', 'Vertretung')
        
        return modified_lesson
    
    def _is_additional_lesson(self, substitution, class_name, regular_lessons):
        """Check if substitution creates an additional lesson not in regular schedule"""
        sub_time = substitution.get('Stunde', substitution.get('Zeit', ''))
        sub_class = substitution.get('Klasse', substitution.get('Klassen', ''))
        
        if class_name not in sub_class:
            return False
        
        # Check if this time slot exists in regular schedule
        for lesson in regular_lessons:
            lesson_time = lesson.get('Zeit', lesson.get('Stunde', ''))
            if lesson_time == sub_time:
                return False
        
        return True
    
    def _create_lesson_from_substitution(self, substitution):
        """Create a new lesson from substitution data"""
        return {
            'Zeit': substitution.get('Stunde', substitution.get('Zeit', '')),
            'Fach': substitution.get('Fach', ''),
            'Lehrer': substitution.get('Lehrer', ''),
            'Raum': substitution.get('Raum', ''),
            'substitution_info': substitution.get('Bemerkung', 'Zusatzstunde')
        }
    
    def export_to_csv(self, filename):
        """Export calculated schedules to CSV"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(['Klasse', 'Datum', 'Zeit', 'Fach', 'Lehrer', 'Raum', 'Bemerkung'])
            
            # Write data
            for class_name, dates in self.calculated_schedules.items():
                for date, lessons in dates.items():
                    for lesson in lessons:
                        writer.writerow([
                            class_name,
                            date,
                            lesson.get('Zeit', ''),
                            lesson.get('Fach', ''),
                            lesson.get('Lehrer', ''),
                            lesson.get('Raum', ''),
                            lesson.get('substitution_info', '')
                        ])

class StundenplanGUI:
    """Main GUI application"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Lanis Stundenplan Rechner")
        self.root.geometry("1000x700")
        
        self.scraper = LanisPortalScraper()
        self.calculator = ScheduleCalculator()
        
        self.setup_gui()
        
        # Load saved credentials
        self.load_credentials()
    
    def setup_gui(self):
        """Setup the GUI elements"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Login Tab
        login_frame = ttk.Frame(notebook)
        notebook.add(login_frame, text="Anmeldung")
        self.setup_login_tab(login_frame)
        
        # Data Tab
        data_frame = ttk.Frame(notebook)
        notebook.add(data_frame, text="Daten")
        self.setup_data_tab(data_frame)
        
        # Results Tab
        results_frame = ttk.Frame(notebook)
        notebook.add(results_frame, text="Ergebnisse")
        self.setup_results_tab(results_frame)
    
    def setup_login_tab(self, parent):
        """Setup login tab"""
        # Credentials frame
        cred_frame = ttk.LabelFrame(parent, text="Lanis Schulportal Zugangsdaten")
        cred_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(cred_frame, text="Schul-ID:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.school_id_var = tk.StringVar()
        ttk.Entry(cred_frame, textvariable=self.school_id_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(cred_frame, text="Benutzername:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.username_var = tk.StringVar()
        ttk.Entry(cred_frame, textvariable=self.username_var, width=30).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(cred_frame, text="Passwort:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.password_var = tk.StringVar()
        ttk.Entry(cred_frame, textvariable=self.password_var, show="*", width=30).grid(row=2, column=1, padx=5, pady=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(cred_frame)
        buttons_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(buttons_frame, text="Anmelden", command=self.login).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Zugangsdaten speichern", command=self.save_credentials).pack(side=tk.LEFT, padx=5)
        
        # Status
        self.status_var = tk.StringVar(value="Nicht angemeldet")
        ttk.Label(cred_frame, textvariable=self.status_var).grid(row=4, column=0, columnspan=2, pady=5)
    
    def setup_data_tab(self, parent):
        """Setup data tab"""
        # Control frame
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(control_frame, text="Vertretungsplan laden", command=self.load_vertretungsplan).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Stundenplan laden", command=self.load_regular_schedule).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Berechnen", command=self.calculate_schedules).pack(side=tk.LEFT, padx=5)
        
        # Data display
        data_notebook = ttk.Notebook(parent)
        data_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Vertretungsplan tab
        vp_frame = ttk.Frame(data_notebook)
        data_notebook.add(vp_frame, text="Vertretungsplan")
        
        self.vp_tree = ttk.Treeview(vp_frame)
        vp_scrollbar = ttk.Scrollbar(vp_frame, orient=tk.VERTICAL, command=self.vp_tree.yview)
        self.vp_tree.configure(yscrollcommand=vp_scrollbar.set)
        self.vp_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vp_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Regular schedule tab
        rs_frame = ttk.Frame(data_notebook)
        data_notebook.add(rs_frame, text="Regulärer Stundenplan")
        
        self.rs_tree = ttk.Treeview(rs_frame)
        rs_scrollbar = ttk.Scrollbar(rs_frame, orient=tk.VERTICAL, command=self.rs_tree.yview)
        self.rs_tree.configure(yscrollcommand=rs_scrollbar.set)
        self.rs_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        rs_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def setup_results_tab(self, parent):
        """Setup results tab"""
        # Control frame
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(control_frame, text="Nach CSV exportieren", command=self.export_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Aktualisieren", command=self.refresh_results).pack(side=tk.LEFT, padx=5)
        
        # Results display
        self.results_tree = ttk.Treeview(parent, columns=('Datum', 'Zeit', 'Fach', 'Lehrer', 'Raum', 'Bemerkung'), show='tree headings')
        
        self.results_tree.heading('#0', text='Klasse')
        self.results_tree.heading('Datum', text='Datum')
        self.results_tree.heading('Zeit', text='Zeit')
        self.results_tree.heading('Fach', text='Fach')
        self.results_tree.heading('Lehrer', text='Lehrer')
        self.results_tree.heading('Raum', text='Raum')
        self.results_tree.heading('Bemerkung', text='Bemerkung')
        
        results_scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=results_scrollbar.set)
        
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
    
    def load_credentials(self):
        """Load credentials from .env file"""
        self.school_id_var.set(os.getenv('LANIS_SCHOOL_ID', ''))
        self.username_var.set(os.getenv('LANIS_USERNAME', ''))
        self.password_var.set(os.getenv('LANIS_PASSWORD', ''))
    
    def save_credentials(self):
        """Save credentials to .env file"""
        try:
            env_content = f"""# Lanis Schulportal Credentials
LANIS_USERNAME={self.username_var.get()}
LANIS_PASSWORD={self.password_var.get()}
LANIS_SCHOOL_ID={self.school_id_var.get()}"""
            
            with open('.env', 'w') as f:
                f.write(env_content)
            
            messagebox.showinfo("Erfolg", "Zugangsdaten wurden gespeichert!")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern: {str(e)}")
    
    def login(self):
        """Login to Lanis Portal"""
        try:
            username = self.username_var.get()
            password = self.password_var.get()
            school_id = self.school_id_var.get()
            
            if not username or not password:
                messagebox.showerror("Fehler", "Bitte Benutzername und Passwort eingeben!")
                return
            
            self.status_var.set("Anmeldung läuft...")
            self.root.update()
            
            success = self.scraper.login(username, password, school_id)
            
            if success:
                self.status_var.set("Erfolgreich angemeldet!")
                messagebox.showinfo("Erfolg", "Anmeldung erfolgreich!")
            else:
                self.status_var.set("Anmeldung fehlgeschlagen!")
                messagebox.showerror("Fehler", "Anmeldung fehlgeschlagen! Bitte Zugangsdaten prüfen.")
                
        except Exception as e:
            self.status_var.set("Fehler bei der Anmeldung!")
            messagebox.showerror("Fehler", f"Fehler bei der Anmeldung: {str(e)}")
    
    def load_vertretungsplan(self):
        """Load Vertretungsplan data"""
        try:
            if not self.scraper.is_logged_in:
                messagebox.showerror("Fehler", "Bitte zuerst anmelden!")
                return
            
            vertretungsplan = self.scraper.get_vertretungsplan()
            
            # Clear existing data
            for item in self.vp_tree.get_children():
                self.vp_tree.delete(item)
            
            if vertretungsplan:
                # Setup columns based on first entry
                if vertretungsplan:
                    columns = list(vertretungsplan[0].keys())
                    self.vp_tree['columns'] = columns
                    self.vp_tree['show'] = 'headings'
                    
                    for col in columns:
                        self.vp_tree.heading(col, text=col)
                        self.vp_tree.column(col, width=100)
                    
                    # Add data
                    for entry in vertretungsplan:
                        values = [entry.get(col, '') for col in columns]
                        self.vp_tree.insert('', tk.END, values=values)
                
                messagebox.showinfo("Erfolg", f"{len(vertretungsplan)} Vertretungsplan-Einträge geladen!")
            else:
                messagebox.showwarning("Warnung", "Keine Vertretungsplan-Daten gefunden!")
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden des Vertretungsplans: {str(e)}")
    
    def load_regular_schedule(self):
        """Load regular schedule data"""
        try:
            if not self.scraper.is_logged_in:
                messagebox.showerror("Fehler", "Bitte zuerst anmelden!")
                return
            
            schedule = self.scraper.get_regular_schedule()
            
            # Clear existing data
            for item in self.rs_tree.get_children():
                self.rs_tree.delete(item)
            
            if schedule:
                self.rs_tree['show'] = 'tree headings'
                self.rs_tree['columns'] = ('Zeit', 'Fach', 'Lehrer', 'Raum')
                
                for col in self.rs_tree['columns']:
                    self.rs_tree.heading(col, text=col)
                    self.rs_tree.column(col, width=100)
                
                # Add data by class
                for class_name, lessons in schedule.items():
                    class_node = self.rs_tree.insert('', tk.END, text=class_name, open=True)
                    
                    for lesson in lessons:
                        values = [
                            lesson.get('Zeit', ''),
                            lesson.get('Fach', ''),
                            lesson.get('Lehrer', ''),
                            lesson.get('Raum', '')
                        ]
                        self.rs_tree.insert(class_node, tk.END, values=values)
                
                messagebox.showinfo("Erfolg", f"Stundenplan für {len(schedule)} Klassen geladen!")
            else:
                messagebox.showwarning("Warnung", "Keine Stundenplan-Daten gefunden!")
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden des Stundenplans: {str(e)}")
    
    def calculate_schedules(self):
        """Calculate schedules with substitutions"""
        try:
            # Get data from scraper
            vertretungsplan = self.scraper.get_vertretungsplan()
            regular_schedule = self.scraper.get_regular_schedule()
            
            if not vertretungsplan and not regular_schedule:
                messagebox.showerror("Fehler", "Keine Daten zum Berechnen vorhanden!")
                return
            
            # Load data into calculator
            self.calculator.load_data(regular_schedule, vertretungsplan)
            
            # Calculate
            calculated = self.calculator.calculate_daily_schedules()
            
            messagebox.showinfo("Erfolg", f"Stundenpläne für {len(calculated)} Klassen berechnet!")
            
            # Refresh results display
            self.refresh_results()
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler bei der Berechnung: {str(e)}")
    
    def refresh_results(self):
        """Refresh results display"""
        try:
            # Clear existing data
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)
            
            # Add calculated data
            for class_name, dates in self.calculator.calculated_schedules.items():
                class_node = self.results_tree.insert('', tk.END, text=class_name, open=True)
                
                for date, lessons in dates.items():
                    date_node = self.results_tree.insert(class_node, tk.END, text=f"  {date}", open=True)
                    
                    for lesson in lessons:
                        values = [
                            date,
                            lesson.get('Zeit', ''),
                            lesson.get('Fach', ''),
                            lesson.get('Lehrer', ''),
                            lesson.get('Raum', ''),
                            lesson.get('substitution_info', '')
                        ]
                        self.results_tree.insert(date_node, tk.END, values=values)
                        
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Aktualisieren der Ergebnisse: {str(e)}")
    
    def export_csv(self):
        """Export results to CSV"""
        try:
            if not self.calculator.calculated_schedules:
                messagebox.showerror("Fehler", "Keine berechneten Daten zum Exportieren!")
                return
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if filename:
                self.calculator.export_to_csv(filename)
                messagebox.showinfo("Erfolg", f"Daten erfolgreich nach {filename} exportiert!")
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Export: {str(e)}")
    
    def run(self):
        """Start the GUI application"""
        try:
            self.root.mainloop()
        finally:
            # Clean up
            self.scraper.close()

def main():
    """Main function"""
    print("Lanis Stundenplan Rechner")
    print("=" * 50)
    
    # Create and run GUI
    app = StundenplanGUI()
    app.run()

if __name__ == "__main__":
    main()