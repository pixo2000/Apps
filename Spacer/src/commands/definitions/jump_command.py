"""
Jump command for Spacer game.
"""
from src.commands.base_command import BaseCommand
from src.functions.navigation_functions import perform_jump
from src.config import WARP_PATHS

class JumpCommand(BaseCommand):
    def __init__(self):
        # Let the base class handle loading from YAML
        super().__init__()
    
    def execute(self, player, args):
        """Execute the jump command"""
        # Validate context
        if not self.validate_context(player):
            return "positive"
        
        # Parse arguments
        dimension_name = args.strip().upper()
        if not dimension_name:
            print(f"\n✗ {self.error_messages['invalid_dimension']}")
            print("Format: jump DIMENSION_NAME")
            return "positive"
        
        # Check if the jump is allowed from current dimension
        current_dim = player.dimension.name
        if current_dim in WARP_PATHS:
            if dimension_name not in WARP_PATHS[current_dim]:
                print(f"\n✗ {self.error_messages['not_connected']}")
                print("Use the 'dimensions' command to see available jump destinations.")
                return "positive"
        
        # Perform the jump
        perform_jump(player, dimension_name)
        return "positive"
