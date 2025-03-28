"""
Command registry for managing all game commands.
"""
import importlib
import os
import pkgutil
from src.commands.base_command import BaseCommand

class CommandRegistry:
    def __init__(self):
        self.commands = {}  # Map of command names to command objects
        self.aliases = {}   # Map of aliases to primary command names
    
    def register(self, command):
        """Register a command in the registry"""
        if not isinstance(command, BaseCommand):
            raise TypeError("Command must be an instance of BaseCommand")
        
        # Register primary command name
        self.commands[command.name] = command
        
        # Register aliases
        for alias in command.aliases:
            if alias in self.aliases:
                print(f"Warning: Alias '{alias}' already exists for another command")
            self.aliases[alias] = command.name
    
    def get_command(self, command_name):
        """Get a command by name or alias"""
        # Check if it's a direct command name
        if command_name in self.commands:
            return self.commands[command_name]
        
        # Check if it's an alias
        if command_name in self.aliases:
            primary_name = self.aliases[command_name]
            return self.commands.get(primary_name)
        
        return None
    
    def load_all_commands(self):
        """Dynamically load all command modules from the definitions directory"""
        # Get the path to the definitions directory
        definitions_path = os.path.join(os.path.dirname(__file__), "definitions")
        
        # Check if the directory exists
        if not os.path.exists(definitions_path):
            print(f"Warning: Command definitions directory not found at {definitions_path}")
            return
        
        # Import all modules in the definitions directory
        command_modules = []
        for _, module_name, is_pkg in pkgutil.iter_modules([definitions_path]):
            if not is_pkg and not module_name.startswith('_'):
                try:
                    module = importlib.import_module(f"src.commands.definitions.{module_name}")
                    command_modules.append(module)
                except ImportError as e:
                    print(f"Error loading command module {module_name}: {e}")
        
        # Find command classes in the imported modules
        for module in command_modules:
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                try:
                    if (isinstance(attr, type) and 
                        issubclass(attr, BaseCommand) and 
                        attr is not BaseCommand):
                        # Create an instance of the command class
                        command_instance = attr()
                        self.register(command_instance)
                except TypeError:
                    # Skip if attr is not a class
                    pass
    
    def handle_command(self, player, input_text):
        """Process user input and execute the corresponding command"""
        if not input_text.strip():
            return "positive"
        
        # Split input into command and arguments
        parts = input_text.split(None, 1)
        command_name = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        # Get the command object
        command = self.get_command(command_name)
        
        # If command not found
        if not command:
            print(f"\n✗ Unknown command: '{command_name}'. Type 'help' for available commands.")
            return "positive"
        
        # Execute the command
        return command.execute(player, args)
