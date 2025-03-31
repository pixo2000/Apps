"""
Launch command for leaving a station or planet surface.
"""
from src.commands.base_command import BaseCommand

class LaunchCommand(BaseCommand):
    def __init__(self):
        # Lade Konfiguration aus der YAML-Datei
        super().__init__()
    
    def execute(self, player, args):
        """Execute the launch command"""
        # Check if player is docked
        if player.docked_at:
            print("\nLaunching from station...")
            player.docked_at = None
            print("You have left the station and returned to space.")
            return "positive"
        
        # Check if player is landed
        if player.landed_on:
            print("\nLaunching from surface...")
            player.landed_on = None
            player.landed_on_body = None
            if hasattr(player, "landed_on_moon"):
                player.landed_on_moon = None
            print("You have successfully returned to orbit.")
            return "positive"
        
        # Not docked or landed
        print("\n✗ You are already in space.")
        return "positive"
