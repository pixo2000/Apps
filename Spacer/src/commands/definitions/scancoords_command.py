"""
Scan coordinates command for scanning specific locations while at a station.
"""
from src.commands.base_command import BaseCommand
from src.commands.scan_commands import handle_coordinate_scan

class ScanCoordsCommand(BaseCommand):
    def __init__(self):
        # Lade Konfiguration aus der YAML-Datei
        super().__init__()
    
    def execute(self, player, args):
        """Execute the scancoords command"""
        # Validate context
        if not self.validate_context(player):
            return "positive"
        
        # Only works at stations
        if not player.docked_at:
            print("\n✗ This command can only be used while docked at a station.")
            return "positive"
        
        # Handle coordinate scan
        handle_coordinate_scan(player, args)
        return "positive"
