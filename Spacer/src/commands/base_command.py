"""
Base command class for Spacer game.
Defines the interface that all commands must implement.
"""

class BaseCommand:
    def __init__(self, name, aliases=None, description="", context_requirements=None, error_messages=None):
        """
        Initialize a command with metadata
        
        Args:
            name (str): Primary command name
            aliases (list): List of alternate names for this command
            description (str): Short description of the command
            context_requirements (list): List of contexts where command can run (e.g., "not_docked")
            error_messages (dict): Dictionary of error messages for different validation failures
        """
        self.name = name
        self.aliases = aliases or []
        self.description = description
        self.context_requirements = context_requirements or []
        self.error_messages = error_messages or {}
    
    def execute(self, player, args):
        """
        Execute the command
        
        Args:
            player: The player object
            args: Command arguments
            
        Returns:
            str: Result status ("positive", "negative", "logout")
        """
        raise NotImplementedError("Subclasses must implement the execute method")
    
    def validate_context(self, player):
        """
        Check if command can be executed in current context
        
        Args:
            player: The player object
            
        Returns:
            bool: True if command can execute, False otherwise
        """
        # Common validation checks
        if "not_docked" in self.context_requirements and player.docked_at:
            print(f"\n✗ {self.error_messages.get('not_docked', 'Cannot execute while docked at a station')}")
            return False
            
        if "not_landed" in self.context_requirements and player.landed_on:
            print(f"\n✗ {self.error_messages.get('not_landed', 'Cannot execute while on planetary surface')}")
            return False
            
        if "not_dead" in self.context_requirements and player.is_dead:
            print("\n☠ You are deceased. Game over.")
            return False
            
        return True
    
    def get_help(self):
        """Return help text for this command"""
        return self.description
