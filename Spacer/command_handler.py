"""
Command parsing and execution for player inputs.
"""
import datetime
import time
from player_actions import PlayerActions
from scanner import handle_scan, scan_celestial_body
from ui_display import display_help, display_discoveries, display_other_player_info
from dimension import Dimension
from save_manager import SaveManager

# Create save manager instance
save_mgr = SaveManager()

def handle_input(player):
    """Process player commands and execute appropriate actions"""
    # Don't accept commands if player is dead
    if player.is_dead:
        print("\n☠ You are deceased. Game over.")
        return "negative"
        
    # Get the raw user input (without converting to lowercase)
    user_input = input(f"\n[{player.position('dimension')}:{player.position('x')},{player.position('y')}] {player.name} > ")
    
    # Create a lowercase version for command detection only
    command_lower = user_input.lower()
    result = "positive"
    
    # Movement command
    if command_lower.startswith("move "):
        parts = user_input.split(" ")
        if len(parts) != 3:
            print("\n✗ Invalid move command. Format: move X Y\n")
            return "positive"
        try:
            x = int(parts[1])
            y = int(parts[2])
            PlayerActions.move(player, x, y)
            return "positive"
        except ValueError:
            print("\n✗ Invalid coordinates. Please enter numbers.\n")
            return "positive"
    
    # Position check command        
    elif command_lower == "whereami":
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
    
    # Dimension jump command        
    elif command_lower.startswith("jump "): 
        dimension_name = user_input.split(" ")[1].upper()
        PlayerActions.jump(player, dimension_name)
        return "positive"
    
    # List dimensions command        
    elif command_lower == "dimensions":
        available = Dimension.get_available_dimensions()
        
        print("\n=== AVAILABLE DIMENSIONS ===")
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
    
    # System scan command        
    elif command_lower == "scan":
        handle_scan(player)
        return "positive"
    
    # Specific body scan command        
    elif command_lower.startswith("scan "):
        # Scan a specific celestial body
        body_name = user_input.split(" ", 1)[1]  # Get everything after "scan "
        scan_celestial_body(player, body_name)
        return "positive"
    
    # Exit game command        
    elif command_lower in ["quit", "exit"]:
        # Save before quitting
        save_mgr.save_game(player)
        print("\n=== SYSTEM SHUTDOWN ===")
        print("Saving data... Done!")
        print("Closing connections...")
        print("\nGoodbye Captain! Safe travels.\n")
        return "negative"
    
    # Help command        
    elif command_lower == "help":
        display_help()
        return "positive"
    
    # Discoveries command        
    elif command_lower == "discoveries":
        display_discoveries(player)
        return "positive"
    
    # Change name command        
    elif command_lower.startswith("changename "):
        # Extract the new name from command, preserving original case
        parts = user_input.split(" ", 1)
        if len(parts) != 2:
            print("\n✗ Invalid command format. Use: changename YourNewName")
            return "positive"
            
        new_name = parts[1]  # Preserves original capitalization
        
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
            
        return "positive"
    
    # Player info command        
    elif command_lower.startswith("playerinfo"):
        parts = user_input.split(None, 1)  # Split by whitespace, max 1 split
        
        if len(parts) > 1:
            # Check another player by name
            other_player_name = parts[1]
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
        return "positive"
    
    # Self destruct command        
    elif command_lower == "self-destruct":
        print("\n⚠ WARNING: Self-destruct sequence initiated!")
        print("⚠ This will permanently kill your character")
        confirm = input("Type 'CONFIRM' to proceed: ")
        
        if confirm == "CONFIRM":
            result = player.kill()
            save_mgr.save_game(player)  # Save dead status
        else:
            print("Self-destruct sequence aborted.")
    
    # Logout command        
    elif command_lower == "logout":
        print("\n=== LOGGING OUT ===")
        print("Saving current session...")
        save_mgr.save_game(player)
        print("Session data saved successfully.")
        print("Returning to login screen...")
        return "logout"  # Special return value for logout
        
    else:
        print("\n✗ Unknown command. Type 'help' for available commands.\n")
    
    # Save after every command (only if not already returning "negative" or "logout")
    if result != "negative" and command_lower != "logout":
        save_mgr.save_game(player)
        
    return result
