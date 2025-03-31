"""
Dimensions command for showing available star systems.
"""
from src.commands.base_command import BaseCommand
from src.config import WARP_PATHS, DIMENSION_DESCRIPTIONS

class DimensionsCommand(BaseCommand):
    def __init__(self):
        # Lade Konfiguration aus der YAML-Datei
        super().__init__()
    
    def execute(self, player, args):
        """Execute the dimensions command"""
        # Validate context
        if not self.validate_context(player):
            return "positive"
        
        # Get current dimension
        current_dim = player.dimension.name
        
        # Get all known dimensions
        known_dims = player.known_dimensions
        
        print("\n== Known Dimensions ==")
        print(f"You are currently in: {current_dim} - {player.dimension.title}")
        
        # List available jump destinations from current dimension
        if current_dim in WARP_PATHS:
            destinations = WARP_PATHS[current_dim]
            if destinations:
                print("\nAvailable jump destinations:")
                for dest in destinations:
                    # Add description if available
                    description = DIMENSION_DESCRIPTIONS.get(dest, "Unknown system")
                    if dest in known_dims:
                        print(f"  {dest} - {description}")
                    else:
                        print(f"  {dest} - {description} (Unexplored)")
            else:
                print("\nNo known jump paths from this dimension.")
        else:
            print("\nNo known jump paths from this dimension.")
        
        return "positive"
