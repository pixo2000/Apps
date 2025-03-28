"""
Scan command for Spacer game.
"""
from src.commands.base_command import BaseCommand
from src.commands.scan_commands import handle_scan_command, handle_specific_scan_command
from src.core.save_manager import SaveManager

# Create save manager for saving after command execution
save_mgr = SaveManager()

class ScanCommand(BaseCommand):
    def __init__(self):
        super().__init__(
            name="scan",
            aliases=["s"],
            description="Scan the current system or a specific body",
            context_requirements=["not_docked", "not_landed", "not_dead"],
            error_messages={
                "not_docked": "Cannot scan while docked at a station. Use 'launch' to undock first.",
                "not_landed": "Cannot scan while on planetary surface. Use 'launch' to return to orbit first.",
            }
        )
    
    def execute(self, player, args):
        """Execute the scan command"""
        # Validate context
        if not self.validate_context(player):
            return "positive"
        
        # Check if it's a general scan or a specific body scan
        if args.strip():
            # Specific body scan
            handle_specific_scan_command(player, args.strip())
        else:
            # General system scan
            handle_scan_command(player)
        
        # Save game after scanning
        save_mgr.save_game(player)
        
        return "positive"
