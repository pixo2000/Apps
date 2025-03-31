"""
Land command for landing on planets or moons.
"""
from src.commands.base_command import BaseCommand
from src.commands.station_commands import handle_land_command

class LandCommand(BaseCommand):
    def __init__(self):
        # Lade Konfiguration aus der YAML-Datei
        super().__init__()
    
    def execute(self, player, args):
        """Execute the land command"""
        # Validate context
        if not self.validate_context(player):
            return "positive"
        
        # Handle landing
        handle_land_command(player)
        return "positive"
