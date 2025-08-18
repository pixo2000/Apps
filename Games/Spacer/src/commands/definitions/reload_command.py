"""
Reload command for refreshing command configurations.
"""
from src.commands.base_command import BaseCommand
from src.commands.registry import cmd_registry

class ReloadCommand(BaseCommand):
    def __init__(self):
        # Let the base class handle loading from YAML
        super().__init__()
    
    def execute(self, player, args):
        """Execute the reload command"""
        print("\nReloading command configurations...")
        count = cmd_registry.reload_all_commands()
        print(f"Successfully reloaded {count} commands.")
        return "positive"
