"""
Logout command for returning to login screen.
"""
from src.commands.base_command import BaseCommand

class LogoutCommand(BaseCommand):
    def __init__(self):
        # Lade Konfiguration aus der YAML-Datei
        super().__init__()
    
    def execute(self, player, args):
        """Execute the logout command"""
        print("\n=== LOGGING OUT ===")
        print("Saving current session...")
        print("Returning to login screen...")
        return "logout"
