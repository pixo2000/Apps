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
        # Let the base class handle loading from YAML
        super().__init__()
    
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
