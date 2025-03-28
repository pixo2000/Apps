"""
Dimensions command for Spacer game.
"""
from src.commands.base_command import BaseCommand
from src.world.dimension import Dimension
from src.config import WARP_PATHS

class DimensionsCommand(BaseCommand):
    def __init__(self):
        super().__init__(
            name="dimensions",
            aliases=["dims", "systems"],
            description="List available dimensions",
            context_requirements=["not_dead"],
            error_messages={}
        )
    
    def execute(self, player, args):
        """Execute the dimensions command"""
        # Validate context
        if not self.validate_context(player):
            return "positive"
        
        available = Dimension.get_available_dimensions()
        current_dim = player.dimension.name
        
        print("\n=== AVAILABLE DIMENSIONS ===")
        # First show dimensions that can be warped to from current location
        if current_dim in WARP_PATHS:
            print(f"\nWarp destinations from {current_dim}:")
            for dim_name in WARP_PATHS[current_dim]:
                try:
                    temp_dim = Dimension(dim_name)
                    discovered = dim_name in player.known_dimensions
                    status = "DISCOVERED" if discovered else "UNDISCOVERED"
                    
                    if discovered:
                        print(f"» {dim_name}: {temp_dim.title} - {temp_dim.description}")
                    else:
                        print(f"» {dim_name}: {status}")
                except Exception as e:
                    print(f"» {dim_name}: ERROR - {str(e)}")
        else:
            print("\nNo warp destinations available from current location.")
        
        # Then show all known dimensions
        print("\nAll known dimensions:")
        for i, dim in enumerate(available):
            try:
                temp_dim = Dimension(dim)
                discovered = dim in player.known_dimensions
                status = "DISCOVERED" if discovered else "UNDISCOVERED"
                
                if discovered:
                    print(f"» {dim}: {temp_dim.title} - {temp_dim.description}")
                else:
                    print(f"» {dim}: {status}")
            except:
                print(f"» {dim}")
        print("===========================\n")
        
        return "positive"
