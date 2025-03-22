"""
Main command router for player inputs.
"""
import datetime
import time
from src.commands.navigation import handle_move_command, handle_jump_command, handle_whereami_command
from src.commands.scan_commands import handle_scan_command, handle_specific_scan_command
from src.commands.station_commands import handle_dock_command, handle_station_input, handle_land_command, handle_planet_input
from src.commands.player_commands import handle_player_info_command, handle_discoveries_command, handle_change_name_command, handle_self_destruct_command
from src.core.save_manager import SaveManager
from src.utils.ui_display import display_help
from src.config import WARP_PATHS

# Create save manager instance
save_mgr = SaveManager()

def handle_input(player):
    """Process player commands and execute appropriate actions"""
    # Check if player is docked at a station
    if player.docked_at:
        return handle_station_input(player)
    
    # Check if player is landed on a planet
    if player.landed_on:
        return handle_planet_input(player)
    
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
            handle_move_command(player, x, y)
            return "positive"
        except ValueError:
            print("\n✗ Invalid coordinates. Please enter numbers.\n")
            return "positive"
    
    # Position check command        
    elif command_lower == "whereami":
        handle_whereami_command(player)
        return "positive"
    
    # Dimension jump command        
    elif command_lower.startswith("jump "): 
        dimension_name = user_input.split(" ")[1].upper()
        handle_jump_command(player, dimension_name)
        return "positive"
    
    # List dimensions command        
    elif command_lower == "dimensions":
        handle_list_dimensions_command(player)
        return "positive"
    
    # System scan command        
    elif command_lower == "scan":
        handle_scan_command(player)
        return "positive"
    
    # Specific body scan command        
    elif command_lower.startswith("scan "):
        # Scan a specific celestial body
        body_name = user_input.split(" ", 1)[1]  # Get everything after "scan "
        handle_specific_scan_command(player, body_name)
        return "positive"
    
    # Dock command to dock at stations
    elif command_lower == "dock":
        handle_dock_command(player)
        return "positive"
        
    # Land command to land on planets or moons
    elif command_lower.startswith("land"):
        handle_land_command(player, command_lower[4:].strip())
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
        handle_discoveries_command(player)
        return "positive"
    
    # Change name command        
    elif command_lower.startswith("changename "):
        # Extract the new name from command, preserving original case
        parts = user_input.split(" ", 1)
        if len(parts) != 2:
            print("\n✗ Invalid command format. Use: changename YourNewName")
            return "positive"
            
        new_name = parts[1]  # Preserves original capitalization
        handle_change_name_command(player, new_name)
        return "positive"
    
    # Player info command        
    elif command_lower.startswith("playerinfo"):
        parts = user_input.split(None, 1)  # Split by whitespace, max 1 split
        
        if len(parts) > 1:
            # Check another player by name
            other_player_name = parts[1]
            handle_player_info_command(player, other_player_name)
        else:
            # Handle showing current player info
            handle_player_info_command(player)
        return "positive"
    
    # Self destruct command        
    elif command_lower == "self-destruct":
        result = handle_self_destruct_command(player)
    
    # Undock/launch commands (only valid when docked/landed)
    elif command_lower == "undock":
        print("\n✗ You are not currently docked at a station.")
        return "positive"
    elif command_lower == "launch":
        print("\n✗ You are not currently on a planetary surface.")
        return "positive"
    
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

def handle_list_dimensions_command(player):
    """Handle the dimensions command to list available dimensions"""
    from src.world.dimension import Dimension
    
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
