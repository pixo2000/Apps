"""
Credits command for Spacer game.
"""
from src.commands.base_command import BaseCommand
from src.commands.player_commands import handle_credits_command

class CreditsCommand(BaseCommand):
    def __init__(self):
        super().__init__(
            name="credits",
            aliases=["about"],
            description="Display game credits",
            context_requirements=[],
            error_messages={}
        )
    
    def execute(self, player, args):
        """Execute the credits command"""
        handle_credits_command()
        return "positive"
