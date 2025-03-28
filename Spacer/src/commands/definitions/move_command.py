"""
Move command for Spacer game.
"""
from src.commands.base_command import BaseCommand
from src.functions.navigation_functions import perform_move
from src.core.save_manager import SaveManager

# Create save manager for saving after command execution
save_mgr = SaveManager()

class MoveCommand(BaseCommand):
    def __init__(self):
        super().__init__(
            name="move",
            aliases=["goto", "nav"],
            description="Move to specific coordinates",
            context_requirements=["not_docked", "not_landed", "not_dead"],
            error_messages={
                "not_docked": "Cannot move while docked at a station. Use 'launch' to undock first.",
                "not_landed": "Cannot move while on planetary surface. Use 'launch' to return to orbit first.",
                "invalid_coords": "Invalid coordinates. Format: move X Y"
            }
        )
    
    def execute(self, player, args):
        """Execute the move command"""
        # Validate context
        if not self.validate_context(player):
            return "positive"
        
        # Parse arguments
        try:
            coords = args.strip().split()
            if len(coords) != 2:
                print(f"\n✗ {self.error_messages['invalid_coords']}")
                return "positive"
            
            x = int(coords[0])
            y = int(coords[1])
        except ValueError:
            print(f"\n✗ {self.error_messages['invalid_coords']}")
            return "positive"
        
        # Perform the move
        success = perform_move(player, x, y)
        
        # Save game after movement
        if success:
            save_mgr.save_game(player)
        
        return "positive"
