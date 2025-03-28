"""
ScanCoords command for Spacer game.
"""
from src.commands.base_command import BaseCommand
from src.commands.scan_commands import handle_coordinate_scan

class ScanCoordsCommand(BaseCommand):
    def __init__(self):
        super().__init__(
            name="scancoords",
            aliases=["sc", "coordinatescan"],
            description="Scan specific coordinates",
            context_requirements=["not_dead"],
            error_messages={
                "not_docked_or_landed": "This command requires station/surface equipment. Must be docked or landed.",
                "invalid_format": "Invalid coordinates format. Use: scancoords <x> <y>"
            }
        )
    
    def execute(self, player, args):
        """Execute the scancoords command"""
        # This command is only available when docked or landed
        if not player.docked_at and not player.landed_on:
            print(f"\n✗ {self.error_messages['not_docked_or_landed']}")
            return "positive"
        
        # Validate args
        if not args.strip():
            print(f"\n✗ {self.error_messages['invalid_format']}")
            return "positive"
        
        # Handle coordinate scan
        handle_coordinate_scan(player, args)
        
        return "positive"
