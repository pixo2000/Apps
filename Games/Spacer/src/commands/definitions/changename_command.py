"""
Change name command for updating player name.
"""
from src.commands.base_command import BaseCommand
from src.commands.player_commands import handle_change_name_command

class ChangenameCommand(BaseCommand):
    def __init__(self):
        # Lade Konfiguration aus der YAML-Datei
        super().__init__()
    
    def execute(self, player, args):
        """Execute the changename command"""
        # Validate context
        if not self.validate_context(player):
            return "positive"
        
        # Check if name is provided
        new_name = args.strip()
        if not new_name:
            print(f"\n✗ {self.error_messages.get('no_name', 'No name provided. Usage: changename <new name>')}")
            return "positive"
        
        # Handle name change
        handle_change_name_command(player, new_name)
        return "positive"
