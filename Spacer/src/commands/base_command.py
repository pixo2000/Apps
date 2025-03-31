"""
Base command class that all game commands inherit from.
"""
import os
import yaml

class BaseCommand:
    def __init__(self, name=None, aliases=None, description=None, context_requirements=None, error_messages=None):
        # Try to load configuration from YAML if not provided
        if name is None:
            config = self._load_config_from_yaml()
            name = config.get('name', self.__class__.__name__.replace('Command', '').lower())
            aliases = config.get('aliases', [])
            description = config.get('description', '')
            context_requirements = config.get('context_requirements', [])
            error_messages = config.get('error_messages', {})
        
        self.name = name
        self.aliases = aliases or []
        self.description = description or ""
        self.context_requirements = context_requirements or []
        self.error_messages = error_messages or {}
    
    def _load_config_from_yaml(self):
        """Load command configuration from YAML file"""
        class_name = self.__class__.__name__.lower()
        command_name = class_name.replace('command', '')
        
        # Build the path to the YAML file
        config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'commands', 'config', 'commands')
        config_path = os.path.join(config_dir, f"{command_name}.yaml")
        
        # Load the YAML file if it exists
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as file:
                    return yaml.safe_load(file) or {}
            except Exception as e:
                print(f"Error loading config for {command_name}: {e}")
        
        # Return empty dict if file doesn't exist
        return {}
    
    def execute(self, player, args):
        """
        Execute the command. Must be implemented by child classes.
        
        Args:
            player: The player object
            args: Command arguments as a string
            
        Returns:
            String indicator of command result ("positive", "negative", or "logout")
        """
        raise NotImplementedError("Command must implement execute method")
    
    def validate_context(self, player):
        """Check if the command can be executed in the current player context"""
        for requirement in self.context_requirements:
            # Not docked requirement
            if requirement == "not_docked" and player.docked_at:
                print(f"\n✗ {self.error_messages.get('not_docked', 'Cannot execute while docked at a station.')}")
                return False
            
            # Not landed requirement
            if requirement == "not_landed" and player.landed_on:
                print(f"\n✗ {self.error_messages.get('not_landed', 'Cannot execute while landed on a planet.')}")
                return False
            
            # Not dead requirement
            if requirement == "not_dead" and player.is_dead:
                print("\n☠ You are deceased. Game over.")
                return False
        
        return True
