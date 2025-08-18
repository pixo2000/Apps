"""
PlayerInfo command for displaying player information.
"""
from src.commands.base_command import BaseCommand
from src.commands.player_commands import handle_player_info_command

class PlayerinfoCommand(BaseCommand):
    def __init__(self):
        # Lade Konfiguration aus der YAML-Datei
        super().__init__()
    
    def execute(self, player, args):
        """Execute the playerinfo command"""
        # Check if we're looking up info for another player
        other_player_name = args.strip()
        handle_player_info_command(player, other_player_name if other_player_name else None)
        return "positive"
