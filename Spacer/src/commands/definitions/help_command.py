"""
Help command for displaying available commands.
"""
from src.commands.base_command import BaseCommand
from src.commands.registry import cmd_registry

class HelpCommand(BaseCommand):
    def __init__(self):
        # Lade Konfiguration aus der YAML-Datei
        super().__init__()
    
    def execute(self, player, args):
        """Execute the help command"""
        command_name = args.strip().lower()
        
        # If a specific command is requested, show detailed help for that command
        if command_name:
            command = cmd_registry.get_command(command_name)
            if command:
                # Show detailed help for the command
                print(f"\n== Help: {command.name.upper()} ==")
                print(f"Description: {command.description}")
                
                # Show aliases if any
                if command.aliases:
                    aliases_str = ", ".join(command.aliases)
                    print(f"Aliases: {aliases_str}")
                
                # Check if there's a help_text in the command's YAML config
                help_text = getattr(command, 'help_text', None)
                if help_text:
                    print(f"\nUsage:\n{help_text}")
                
                return "positive"
            else:
                print(f"\n✗ {self.error_messages.get('unknown_command', 'Unknown command')}")
                return "positive"
        
        # Otherwise, show a list of all available commands
        print("\n== Available Commands ==")
        
        # Get all commands from registry
        all_commands = {}
        for cmd_name, cmd_obj in cmd_registry.commands.items():
            all_commands[cmd_name] = cmd_obj
        
        # Sort commands by name
        sorted_commands = sorted(all_commands.items())
        
        # Display commands and their descriptions
        for name, cmd in sorted_commands:
            print(f"{name.ljust(12)} - {cmd.description}")
        
        print("\nType 'help <command>' for more information on a specific command.")
        return "positive"
