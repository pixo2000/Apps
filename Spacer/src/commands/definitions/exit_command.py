"""
Exit command for quitting the game.
"""
from src.commands.base_command import BaseCommand

class ExitCommand(BaseCommand):
    def __init__(self):
        # Lade Konfiguration aus der YAML-Datei
        super().__init__()
    
    def execute(self, player, args):
        """Execute the exit command"""
        print("\n=== SYSTEM SHUTDOWN ===")
        print("Saving game state... Done!")
        print("Closing connections...")
        print("\nGoodbye Captain! Safe travels.\n")
        return "negative"
