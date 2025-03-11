import player
from dimension import Dimension
from player_functions import scan_system, display_scan_results
from save_manager import SaveManager
import json  # Neuer Import für JSON-Verarbeitung

# Create save manager instance
save_mgr = SaveManager()

def handle_input(name):
    # Don't accept commands if player is dead
    if name.is_dead:
        print("\n☠ You are deceased. Game over.")
        return "negative"
        
    # Get the raw user input (without converting to lowercase)
    user_input = input(f"\n[{name.position('dimension')}:{name.position('x')},{name.position('y')}] {name.name} > ")
    
    # Create a lowercase version for command detection only
    command_lower = user_input.lower()
    result = "positive"
    
    if command_lower.startswith("move "):
        parts = user_input.split(" ")
        if len(parts) != 3:
            print("\n✗ Invalid move command. Format: move X Y\n")
            return "positive"
        try:
            x = int(parts[1])
            y = int(parts[2])
            name.move(x,y)
            return "positive"
        except ValueError:
            print("\n✗ Invalid coordinates. Please enter numbers.\n")
            return "positive"
            
    elif command_lower == "whereami":
        dimension = name.position('dimension')
        x_pos = name.position('x')
        y_pos = name.position('y')
        
        print("\n=== CURRENT LOCATION ===")
        print(f"» Dimension: {dimension}")
        print(f"» Coordinates: [{x_pos}, {y_pos}]")
        try:
            dim_title = name.dimension.title
            print(f"» System: {dim_title}")
        except AttributeError:
            pass
        print("=======================\n")
        return "positive"
        
    elif command_lower.startswith("jump "): 
        dimension_name = user_input.split(" ")[1].upper()
        name.jump(dimension_name)
        return "positive"
        
    elif command_lower == "dimensions":
        available = Dimension.get_available_dimensions()
        
        print("\n=== AVAILABLE DIMENSIONS ===")
        for i, dim in enumerate(available):
            try:
                temp_dim = Dimension(dim)
                discovered = dim in name.known_dimensions
                status = "DISCOVERED" if discovered else "UNDISCOVERED"
                
                if discovered:
                    print(f"» {dim}: {temp_dim.title} - {temp_dim.description}")
                else:
                    print(f"» {dim}: {status}")
            except:
                print(f"» {dim}")
        print("===========================\n")
        return "positive"
        
    elif command_lower == "scan":
        scan_results = scan_system(name)
        display_scan_results(scan_results)
        return "positive"
        
    elif command_lower in ["quit", "exit"]:
        # Save before quitting
        save_mgr.save_game(name)
        print("\n=== SYSTEM SHUTDOWN ===")
        print("Saving data... Done!")
        print("Closing connections...")
        print("\nGoodbye Captain! Safe travels.\n")
        return "negative"
        
    elif command_lower == "help":
        display_help()
        return "positive"
        
    elif command_lower == "discoveries":
        display_discoveries(name)
        return "positive"
        
    elif command_lower.startswith("changename "):
        # Extract the new name from command, preserving original case
        parts = user_input.split(" ", 1)
        if len(parts) != 2:
            print("\n✗ Invalid command format. Use: changename YourNewName")
            return "positive"
            
        new_name = parts[1]  # This now preserves the original capitalization
        
        # Attempt to change the player's name
        success, message = save_mgr.change_player_name(name, new_name)
        
        if success:
            print(f"\n✓ {message}")
            print(f"✓ Your unique player ID remains: {name.uuid}")
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
        
    elif command_lower.startswith("playerinfo"):
        parts = user_input.split(None, 1)  # Split by whitespace, max 1 split
        
        if len(parts) > 1:
            # Check another player by name
            other_player_name = parts[1]
            display_other_player_info(other_player_name)
        else:
            # Show current player info
            print("\n=== PLAYER INFORMATION ===")
            print(f"» Name: {name.name}")
            print(f"» UUID: {name.uuid}")
            print(f"» Status: {'Alive' if not name.is_dead else 'Deceased'}")
            print(f"» Current Dimension: {name.dimension.name} ({name.dimension.title})")
            print(f"» Position: [{name.x}, {name.y}]")
            print(f"» Dimensions visited: {len(name.known_dimensions)}")
            
            # Count total discovered bodies
            total_bodies = sum(len(bodies) for bodies in name.known_bodies.values())
            print(f"» Celestial bodies discovered: {total_bodies}")
            print("=========================\n")
        return "positive"
        
    elif command_lower == "self-destruct":
        print("\n⚠ WARNING: Self-destruct sequence initiated!")
        print("⚠ This will permanently kill your character")
        confirm = input("Type 'CONFIRM' to proceed: ")
        
        if confirm == "CONFIRM":
            result = name.kill()
            save_mgr.save_game(name)  # Save dead status
        else:
            print("Self-destruct sequence aborted.")
        
    elif command_lower == "logout":
        print("\n=== LOGGING OUT ===")
        print("Saving current session...")
        save_mgr.save_game(name)
        print("Session data saved successfully.")
        print("Returning to login screen...")
        return "logout"  # New special return value for logout
        
    else:
        print("\n✗ Unknown command. Type 'help' for available commands.\n")
    
    # Save after every command (only if not already returning "negative" or "logout")
    if result != "negative" and command_lower != "logout":
        save_mgr.save_game(name)
    return result

def display_help(first_time=False):
    print("\n" + "=" * 50)
    print("             COMMAND REFERENCE")
    print("=" * 50)
    
    if first_time:
        print("\n👋 Welcome, new Captain! Here are the commands to get you started:\n")
    
    commands = [
        ("move X Y", "Navigate to coordinates X, Y"),
        ("whereami", "Display current location information"),
        ("jump DIM", "Jump to dimension DIM (e.g. A01, C12)"),
        ("dimensions", "List all available dimensions"),
        ("scan", "Scan current system for celestial bodies"),
        ("discoveries", "Display all your discoveries"),
        ("changename NAME", "Change your captain's name"),
        ("playerinfo [NAME]", "Display player info (yours or another captain)"),
        ("logout", "Save and log out to switch captains"),
        ("self-destruct", "End your journey permanently"),
        ("quit/exit", "Exit the game"),
        ("help", "Display this help message")
    ]
    
    for cmd, desc in commands:
        print(f"» {cmd.ljust(15)} - {desc}")
    
    if first_time:
        print("\n💡 TIP: Start by typing 'scan' to discover nearby celestial bodies")
        print("   or 'dimensions' to see what star systems you can visit!")
    
    print("=" * 50 + "\n")

def display_discoveries(player):
    print("\n" + "=" * 50)
    print("             YOUR DISCOVERIES")
    print("=" * 50)
    
    print(f"\nDimensions visited: {len(player.known_dimensions)}")
    for dim_name in player.known_dimensions:
        try:
            dim = Dimension(dim_name)
            bodies_count = len(player.known_bodies.get(dim_name, []))
            print(f"\n» {dim_name}: {dim.title}")
            print(f"  {dim.description}")
            print(f"  Discovered bodies: {bodies_count}")
            
            if bodies_count > 0:
                for body in player.known_bodies[dim_name]:
                    print(f"   - {body}")
        except:
            print(f"» {dim_name}: [Data corrupted]")
    
    print("\n" + "=" * 50)

def display_other_player_info(player_name):
    """Display information about another player by name"""
    print("\n=== PLAYER INFORMATION ===")
    
    # Get player data from save files
    player_data = None
    for save_file in save_mgr.save_directory.glob('*.json'):
        try:
            with open(save_file, 'r') as f:
                data = json.load(f)
                if data.get("name", "").lower() == player_name.lower():
                    player_data = data
                    break
        except:
            continue
    
    if not player_data:
        print(f"» Captain '{player_name}' not found in records.")
        print("=========================\n")
        return
        
    print(f"» Name: {player_data['name']}")
    
    # Show UUID
    if "uuid" in player_data:
        print(f"» UUID: {player_data['uuid']}")
    
    # Show status (alive/deceased)
    status = "Alive" if not player_data.get("is_dead", False) else "Deceased"
    print(f"» Status: {status}")
    
    # Only show discovery stats if player is not dead
    if not player_data.get("is_dead", False):
        # Show discoveries stats
        try:
            dims_visited = len(player_data["discoveries"]["known_dimensions"])
            print(f"» Dimensions visited: {dims_visited}")
        except:
            print("» Dimensions visited: Unknown")
        
        # Count total bodies
        try:
            known_bodies = player_data["discoveries"]["known_bodies"]
            total_bodies = sum(len(bodies) for bodies in known_bodies.values())
            print(f"» Celestial bodies discovered: {total_bodies}")
        except:
            print("» Celestial bodies discovered: Unknown")
    
    print("=========================\n")