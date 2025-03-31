"""
Scan command for detecting celestial bodies.
"""
from src.commands.base_command import BaseCommand
from src.commands.scan_commands import handle_scan_command, handle_specific_scan_command

class ScanCommand(BaseCommand):
    def __init__(self):
        # Lade Konfiguration aus der YAML-Datei
        super().__init__()
    
    def execute(self, player, args):
        """Execute the scan command"""
        # Validate context
        if not self.validate_context(player):
            return "positive"
        
        # Check if we're scanning a specific body or doing a general scan
        body_name = args.strip()
        if body_name:
            # Scan specific celestial body
            handle_specific_scan_command(player, body_name)
        else:
            # General system scan
            handle_scan_command(player)
            
        return "positive"
