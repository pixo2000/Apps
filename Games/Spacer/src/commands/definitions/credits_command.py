"""
Credits command for displaying game credits.
"""
from src.commands.base_command import BaseCommand

class CreditsCommand(BaseCommand):
    def __init__(self):
        # Lade Konfiguration aus der YAML-Datei
        super().__init__()
    
    def execute(self, player, args):
        """Execute the credits command"""
        print("\n== SPACER: INTERSTELLAR EXPLORATION SIMULATOR ==")
        print("\nDeveloped by: LU\n")
        print("A text-based space exploration game written in Python")
        print("Version: Alpha 0.1\n")
        print("Special thanks to all testers and contributors!")
        print("=========================================")
        
        return "positive"
