"""
Discoveries command for Spacer game.
"""
from src.commands.base_command import BaseCommand
from src.commands.player_commands import handle_discoveries_command

class DiscoveriesCommand(BaseCommand):
    def __init__(self):
        super().__init__(
            name="discoveries",
            aliases=["disc", "found", "log"],
            description="Display discovered celestial bodies",
            context_requirements=["not_dead"],
            error_messages={}
        )
    
    def execute(self, player, args):
        """Execute the discoveries command"""
        # Validate context
        if not self.validate_context(player):
            return "positive"
        
        # Handle discoveries command
        handle_discoveries_command(player)
        
        return "positive"
