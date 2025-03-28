"""
Logout command for Spacer game.
"""
from src.commands.base_command import BaseCommand
from src.core.save_manager import SaveManager

# Create save manager for saving before logout
save_mgr = SaveManager()

class LogoutCommand(BaseCommand):
    def __init__(self):
        super().__init__(
            name="logout",
            aliases=["signout"],
            description="Save and return to login screen",
            context_requirements=[],
            error_messages={}
        )
    
    def execute(self, player, args):
        """Execute the logout command"""
        print("\n=== LOGGING OUT ===")
        print("Saving current session...")
        save_mgr.save_game(player)
        print("Session data saved successfully.")
        print("Returning to login screen...")
        
        return "logout"
