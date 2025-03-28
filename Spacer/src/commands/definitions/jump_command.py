"""
Jump command for Spacer game.
"""
from src.commands.base_command import BaseCommand
from src.functions.navigation_functions import perform_jump
from src.config import WARP_PATHS

class JumpCommand(BaseCommand):
    def __init__(self):
        super().__init__(
            name="jump",
            aliases=["j", "warp"],
            description="Jump to another star system",
            context_requirements=["not_docked", "not_landed", "not_dead"],
            error_messages={
                "not_docked": "Cannot jump while docked at a station. Use 'launch' to undock first.",
                "not_landed": "Cannot jump while on planetary surface. Use 'launch' to return to orbit first.",
                "invalid_dimension": "Invalid dimension name",
                "not_connected": "Cannot jump directly to that dimension from here"
            }
        )
    
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
