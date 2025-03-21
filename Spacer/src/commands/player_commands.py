"""
Player information and account management commands.
"""
import datetime
from src.core.save_manager import SaveManager
from src.utils.ui_display import display_discoveries, display_other_player_info

# Create save manager instance
save_mgr = SaveManager()

def handle_player_info_command(player, other_player_name=None):
    """Handle player info command, either for current player or another player"""
    if other_player_name:
        # Show info about another player
        display_other_player_info(other_player_name)
    else:
        # Save game data first to ensure playtime is accurate
        # Calculate current session playtime and add it to total
        current_time = datetime.datetime.now()
        if hasattr(player, "session_start"):
            session_duration = (current_time - player.session_start).total_seconds()
            player.playtime += session_duration
            # Update session start time for future calculations
            player.session_start = current_time
        
        # Save the updated data
        save_mgr.save_game(player)
        
        # Show current player info
        print("\n=== PLAYER INFORMATION ===")
        print(f"» Name: {player.name}")
        print(f"» UUID: {player.uuid}")
        print(f"» Status: {'Alive' if not player.is_dead else 'Deceased'}")
        print(f"» Current Dimension: {player.dimension.name} ({player.dimension.title})")
        print(f"» Position: [{player.x}, {player.y}]")
        print(f"» Dimensions visited: {len(player.known_dimensions)}")
        
        # Count total discovered bodies
        total_bodies = sum(len(bodies) for bodies in player.known_bodies.values())
        print(f"» Celestial bodies discovered: {total_bodies}")
        
        # Display playtime from player object
        if hasattr(player, "playtime"):
            # Get formatted playtime from save_mgr
            playtime = save_mgr.format_playtime(player.playtime)
            print(f"» Total playtime: {playtime}")
        
        # Display creation date and last login if available
        if hasattr(player, "creation_date"):
            creation_date = save_mgr.format_date(player.creation_date)
            print(f"» Created: {creation_date}")
        
        print("=========================\n")

def handle_discoveries_command(player):
    """Handle the discoveries command to show discovered objects"""
    display_discoveries(player)

def handle_change_name_command(player, new_name):
    """Handle the changename command to rename the player"""
    # Attempt to change the player's name
    success, message = save_mgr.change_player_name(player, new_name)
    
    if success:
        print(f"\n✓ {message}")
        print(f"✓ Your unique player ID remains: {player.uuid}")
    else:
        print(f"\n✗ Failed to change name: {message}")
        # Add more detailed error message if name format is invalid
        if "Invalid name format" in message:
            print("  Names must be 3-15 characters long and can contain:")
            print("  - Uppercase letters (A-Z)")
            print("  - Lowercase letters (a-z)")
            print("  - Numbers (0-9)")
            print("  - Underscores (_)")

def handle_self_destruct_command(player):
    """Handle the self-destruct command that kills the player"""
    print("\n⚠ WARNING: Self-destruct sequence initiated!")
    print("⚠ This will permanently kill your character")
    confirm = input("Type 'CONFIRM' to proceed: ")
    
    if confirm == "CONFIRM":
        result = player.kill()
        save_mgr.save_game(player)  # Save dead status
        return "negative"  # Exit game after self-destruct
    else:
        print("Self-destruct sequence aborted.")
        return "positive"
