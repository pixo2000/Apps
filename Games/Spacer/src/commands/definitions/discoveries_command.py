"""
Discoveries command for displaying discovered celestial bodies.
"""
from src.commands.base_command import BaseCommand
from src.commands.player_commands import handle_discoveries_command

class DiscoveriesCommand(BaseCommand):
    def __init__(self):
        # Lade Konfiguration aus der YAML-Datei
        super().__init__()
    
    def execute(self, player, args):
        """Execute the discoveries command"""
        # Validate context
        if not self.validate_context(player):
            return "positive"
        
        # Handle discoveries display
        handle_discoveries_command(player)
        return "positive"
