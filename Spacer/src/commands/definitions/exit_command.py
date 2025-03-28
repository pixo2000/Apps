"""
Exit/Quit command for Spacer game.
"""
from src.commands.base_command import BaseCommand
from src.core.save_manager import SaveManager

# Create save manager for saving before exit
save_mgr = SaveManager()

class ExitCommand(BaseCommand):
    def __init__(self):
        super().__init__(
            name="exit",
            aliases=["quit", "q"],
            description="Save and exit the game",
            context_requirements=[],
            error_messages={}
        )
    
    def execute(self, player, args):
        """Execute the exit command"""
        # Save before quitting
        save_mgr.save_game(player)
        print("\n=== SYSTEM SHUTDOWN ===")
        print("Saving data... Done!")
        print("Closing connections...")
        print("\nGoodbye Captain! Safe travels.\n")
        
        return "negative"
