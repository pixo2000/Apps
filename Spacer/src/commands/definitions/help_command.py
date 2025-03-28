"""
Help command for Spacer game.
"""
from src.commands.base_command import BaseCommand
from src.utils.ui_display import display_help

class HelpCommand(BaseCommand):
    def __init__(self):
        super().__init__(
            name="help",
            aliases=["h", "?"],
            description="Display help information",
            context_requirements=[],
            error_messages={}
        )
    
    def execute(self, player, args):
        """Execute the help command"""
        display_help(first_time=False)
        return "positive"
