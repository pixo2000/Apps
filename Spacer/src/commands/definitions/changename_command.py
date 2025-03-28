"""
ChangeName command for Spacer game.
"""
from src.commands.base_command import BaseCommand
from src.commands.player_commands import handle_change_name_command

class ChangeNameCommand(BaseCommand):
    def __init__(self):
        super().__init__(
            name="changename",
            aliases=["rename"],
            description="Change your captain name",
            context_requirements=["not_dead"],
            error_messages={
                "invalid_format": "Invalid command format. Use: changename YourNewName"
            }
        )
    
    def execute(self, player, args):
        """Execute the changename command"""
        # Validate context
        if not self.validate_context(player):
            return "positive"
        
        # Check if new name is provided
        new_name = args.strip()
        if not new_name:
            print(f"\n✗ {self.error_messages['invalid_format']}")
            return "positive"
        
        # Handle change name command
        handle_change_name_command(player, new_name)
        
        return "positive"
