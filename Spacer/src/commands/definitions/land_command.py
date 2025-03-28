"""
Land command for Spacer game.
"""
from src.commands.base_command import BaseCommand
from src.commands.station_commands import handle_land_command
from src.core.save_manager import SaveManager

# Create save manager for saving after command execution
save_mgr = SaveManager()

class LandCommand(BaseCommand):
    def __init__(self):
        super().__init__(
            name="land",
            aliases=["touchdown"],
            description="Land on a planet or moon",
            context_requirements=["not_docked", "not_landed", "not_dead"],
            error_messages={
                "not_docked": "Cannot land while docked at a station. Use 'launch' to undock first.",
                "not_landed": "You are already on a planetary surface."
            }
        )
    
    def execute(self, player, args):
        """Execute the land command"""
        # Validate context
        if not self.validate_context(player):
            return "positive"
        
        # Handle landing
        handle_land_command(player, args.strip())
        
        # Save game state after landing
        save_mgr.save_game(player)
        
        return "positive"
