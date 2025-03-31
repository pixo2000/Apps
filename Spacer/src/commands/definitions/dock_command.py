"""
Dock command for docking at stations.
"""
from src.commands.base_command import BaseCommand
from src.commands.station_commands import handle_dock_command

class DockCommand(BaseCommand):
    def __init__(self):
        # Lade Konfiguration aus der YAML-Datei
        super().__init__()
    
    def execute(self, player, args):
        """Execute the dock command"""
        # Validate context
        if not self.validate_context(player):
            return "positive"
        
        # Handle docking
        handle_dock_command(player)
        return "positive"
