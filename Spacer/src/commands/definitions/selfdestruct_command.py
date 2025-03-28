"""
Self-Destruct command for Spacer game.
"""
from src.commands.base_command import BaseCommand
from src.commands.player_commands import handle_self_destruct_command

class SelfDestructCommand(BaseCommand):
    def __init__(self):
        super().__init__(
            name="self-destruct",
            aliases=["selfdestruct", "sd"],
            description="Initiate self-destruct sequence (kills your character)",
            context_requirements=["not_dead"],
            error_messages={}
        )
    
    def execute(self, player, args):
        """Execute the self-destruct command"""
        # Validate context
        if not self.validate_context(player):
            return "positive"
        
        # Handle self-destruct command
        result = handle_self_destruct_command(player)
        return result
