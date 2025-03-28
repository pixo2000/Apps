"""
Whereami command for Spacer game.
"""
from src.commands.base_command import BaseCommand
from src.core.save_manager import SaveManager

# Create save manager for saving after command execution
save_mgr = SaveManager()

class WhereAmICommand(BaseCommand):
    def __init__(self):
        super().__init__(
            name="whereami",
            aliases=["location", "pos", "position"],
            description="Display your current location",
            context_requirements=["not_dead"],
            error_messages={}
        )
    
    def execute(self, player, args):
        """Execute the whereami command"""
        # Validate context
        if not self.validate_context(player):
            return "positive"
        
        dimension = player.position('dimension')
        x_pos = player.position('x')
        y_pos = player.position('y')
        
        print("\n=== CURRENT LOCATION ===")
        print(f"» Dimension: {dimension}")
        print(f"» Coordinates: [{x_pos}, {y_pos}]")
        try:
            dim_title = player.dimension.title
            print(f"» System: {dim_title}")
        except AttributeError:
            pass
        print("=======================\n")
        
        return "positive"
