"""
PlayerInfo command for Spacer game.
"""
from src.commands.base_command import BaseCommand
from src.commands.player_commands import handle_player_info_command
from src.core.save_manager import SaveManager

# Create save manager for saving after command execution
save_mgr = SaveManager()

class PlayerInfoCommand(BaseCommand):
    def __init__(self):
        super().__init__(
            name="playerinfo",
            aliases=["pi", "info", "stats"],
            description="Display player information",
            context_requirements=["not_dead"],
            error_messages={}
        )
    
    def execute(self, player, args):
        """Execute the playerinfo command"""
        # Validate context
        if not self.validate_context(player):
            return "positive"
        
        # Get other player name if provided
        other_player_name = args.strip() if args.strip() else None
        
        # Handle player info command
        handle_player_info_command(player, other_player_name)
        
        return "positive"
