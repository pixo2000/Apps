"""
Dock command for Spacer game.
"""
from src.commands.base_command import BaseCommand
from src.commands.station_commands import handle_dock_command
from src.core.save_manager import SaveManager

# Create save manager for saving after command execution
save_mgr = SaveManager()

class DockCommand(BaseCommand):
    def __init__(self):
        super().__init__(
            name="dock",
            aliases=["board"],
            description="Dock at a station",
            context_requirements=["not_docked", "not_landed", "not_dead"],
            error_messages={
                "not_docked": "You are already docked at a station.",
                "not_landed": "Cannot dock while on planetary surface. Use 'launch' to return to orbit first."
            }
        )
    
    def execute(self, player, args):
        """Execute the dock command"""
        # Validate context
        if not self.validate_context(player):
            return "positive"
        
        # Handle docking
        handle_dock_command(player)
        
        # Save game state after docking
        save_mgr.save_game(player)
        
        return "positive"
