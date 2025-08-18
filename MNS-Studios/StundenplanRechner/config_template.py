# Configuration file for Lanis Stundenplan Rechner
# Copy this file to config.py and adjust the settings as needed

# Lanis Portal URLs
LANIS_BASE_URL = "https://connect.schulportal.hessen.de"
LANIS_LOGIN_URL = f"{LANIS_BASE_URL}/login.php"
LANIS_VERTRETUNGSPLAN_URL = f"{LANIS_BASE_URL}/vertretungsplan.php"
LANIS_STUNDENPLAN_URL = f"{LANIS_BASE_URL}/stundenplan.php"

# Browser settings for Selenium
BROWSER_SETTINGS = {
    "headless": True,  # Set to False to see browser window
    "window_size": "1920,1080",
    "timeout": 10,  # seconds
    "implicit_wait": 5  # seconds
}

# Application settings
APP_SETTINGS = {
    "auto_refresh_interval": 300,  # seconds (5 minutes)
    "max_retries": 3,
    "export_format": "csv",  # csv, json, excel
    "date_format": "%d.%m.%Y",
    "time_format": "%H:%M"
}

# GUI settings
GUI_SETTINGS = {
    "window_title": "Lanis Stundenplan Rechner",
    "window_size": "1000x700",
    "theme": "default",  # default, dark, light
    "font_size": 10
}

# Data processing settings
DATA_SETTINGS = {
    "classes_to_include": [],  # Empty list means all classes, or specify like ["9A", "10B"]
    "subjects_to_exclude": [],  # Subjects to ignore, e.g., ["Pause", "Freistunde"]
    "teachers_to_highlight": [],  # Teachers to highlight in results
    "rooms_to_monitor": []  # Specific rooms to monitor for changes
}

# Logging settings
LOGGING_SETTINGS = {
    "level": "INFO",  # DEBUG, INFO, WARNING, ERROR
    "log_to_file": False,
    "log_file": "stundenplan_rechner.log",
    "max_log_size": 10485760,  # 10MB
    "backup_count": 5
}

# Export settings
EXPORT_SETTINGS = {
    "default_filename": "stundenplan_export",
    "include_timestamp": True,
    "csv_delimiter": ",",
    "csv_encoding": "utf-8-sig"  # For Excel compatibility
}

# Security settings
SECURITY_SETTINGS = {
    "save_credentials": True,  # Whether to allow saving credentials
    "encrypt_credentials": False,  # Future feature
    "session_timeout": 3600  # seconds (1 hour)
}

# Field mappings for different Lanis versions
# Adjust these if your school's Lanis portal uses different field names
FIELD_MAPPINGS = {
    "time": ["Zeit", "Stunde", "Std"],
    "subject": ["Fach", "Unterrichtsfach"],
    "teacher": ["Lehrer", "Lehrkraft", "LK"],
    "room": ["Raum", "Zimmer"],
    "class": ["Klasse", "Klassen"],
    "comment": ["Bemerkung", "Hinweis", "Info"],
    "date": ["Datum", "Tag"]
}

# CSS selectors for web scraping
# Update these if the Lanis portal structure changes
CSS_SELECTORS = {
    "login_form": "form[name='login']",
    "username_field": "input[name='user']",
    "password_field": "input[name='password']",
    "school_id_field": "input[name='schulnummer']",
    "login_button": "input[type='submit']",
    "vertretung_table": "table.vertretung, table.mon_list",
    "stundenplan_table": "table.KlStdPlan, table.stundenplan"
}

# Error messages
ERROR_MESSAGES = {
    "login_failed": "Anmeldung fehlgeschlagen. Bitte Zugangsdaten prüfen.",
    "no_data": "Keine Daten gefunden. Möglicherweise ist das Portal nicht erreichbar.",
    "network_error": "Netzwerkfehler. Bitte Internetverbindung prüfen.",
    "parsing_error": "Fehler beim Verarbeiten der Daten. Das Portal könnte geändert worden sein.",
    "export_error": "Fehler beim Exportieren der Daten."
}

# Success messages
SUCCESS_MESSAGES = {
    "login_success": "Erfolgreich angemeldet!",
    "data_loaded": "Daten erfolgreich geladen!",
    "calculation_complete": "Stundenplan-Berechnung abgeschlossen!",
    "export_complete": "Export erfolgreich abgeschlossen!"
}
