"""
Self-destruct command for ending the current player's game.
"""
import time
from src.commands.base_command import BaseCommand

class SelfDestructCommand(BaseCommand):
    def __init__(self):
        # Lade Konfiguration aus der YAML-Datei
        super().__init__()
    
    def execute(self, player, args):
        """Execute the self-destruct command"""
        # Validate context
        if not self.validate_context(player):
            return "positive"
            
        # Ask for confirmation
        print("\n⚠ WARNING: Self-destruct sequence initiated ⚠")
        print("This will permanently kill your character. All progress will be lost.")
        confirmation = input("Type 'CONFIRM' to proceed: ")
        
        if confirmation != "CONFIRM":
            print("\nSelf-destruct sequence aborted.")
            return "positive"
            
        # Countdown animation
        print("\n⚠ SELF-DESTRUCT SEQUENCE ACTIVATED ⚠")
        for i in range(5, 0, -1):
            print(f"    {i}...", flush=True)
            time.sleep(1)
        
        # Kill the player
        player.kill()
        
        # Return negative to exit the game
        return "negative"
