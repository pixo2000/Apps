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
from station import get_station_at_coords, STATIONS

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
    
    # Dock command to dock at stations
    elif command_lower == "dock":
        handle_dock_command(player, None)
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

def handle_station_input(player):
    """Handle input while docked at a station"""
    # Display station options only once when first docking
    if not hasattr(player, "_station_options_shown") or player._station_options_shown != player.docked_at.name:
        player.docked_at.display_options()
        player._station_options_shown = player.docked_at.name
    
    user_input = input(f"\n[ {player.docked_at.name} ]> ").strip().lower()
    
    if user_input == "exit" or user_input == "quit":
        return "negative"
    
    if user_input == "logout":
        return "logout"
    
    if user_input == "help":
        # Show station-specific help
        print("\n== Station Help ==")
        print("You are currently docked at a station. Available commands:")
        for cmd, desc in player.docked_at.available_options.items():
            print(f"  {cmd.ljust(10)} - {desc}")
        print("\nGeneral commands:")
        print("  help       - Show this help message")
        print("  logout     - Save and return to login screen")
        print("  exit/quit  - Save and exit game")
        return True
    
    # Handle the options command to re-display the options
    if user_input == "options":
        player.docked_at.display_options()
        return True
    
    # Try to handle command with station
    if player.docked_at.handle_command(user_input, player):
        return True
    
    print(f"Unknown station command: '{user_input}'. Type 'help' for available commands or 'options' to see all options.")
    return True

def handle_planet_input(player):
    """Handle input while landed on a planet or moon"""
    planet_name = player.landed_on
    print(f"\n== Surface of {planet_name} ==")
    print("Available commands:")
    print("  explore    - Explore the surroundings")
    print("  launch     - Return to orbit")
    print("  analyze    - Analyze surface composition")
    print("  help       - Show this help message")
    print("  logout     - Save and return to login screen")
    print("  exit/quit  - Save and exit game")
    
    user_input = input("\nSurface> ").strip().lower()
    
    if user_input == "exit" or user_input == "quit":
        return "negative"
    
    if user_input == "logout":
        return "logout"
    
    if user_input == "help":
        # Show planet-specific help
        print("\n== Surface Operations Help ==")
        print(f"You are currently on the surface of {planet_name}. Available commands:")
        print("  explore    - Explore the surroundings for resources and discoveries")
        print("  launch     - Return to orbit and resume space travel")
        print("  analyze    - Perform detailed analysis of surface composition")
        print("\nGeneral commands:")
        print("  help       - Show this help message")
        print("  logout     - Save and return to login screen")
        print("  exit/quit  - Save and exit game")
        return True
    
    elif user_input == "launch":
        print(f"\nLaunching from the surface of {planet_name}...")
        time.sleep(1)
        player.landed_on = None
        print("You have successfully returned to orbit.")
        return True
    
    elif user_input == "explore":
        print("\n== Exploration Results ==")
        # This could be expanded with random events, resources, or discoveries
        results = ["Found some interesting geological formations.",
                  "Discovered traces of ancient structures.",
                  "Mapped an unusual terrain pattern.",
                  "Found nothing of interest this time.",
                  "Detected unusual energy readings from nearby."]
        
        import random
        print(random.choice(results))
        return True
    
    elif user_input == "analyze":
        print("\n== Surface Analysis ==")
        print("Analyzing surface composition...")
        time.sleep(1)
        
        # Get planet data from player's known bodies if available
        planet_data = None
        for dim_name, bodies in player.known_bodies.items():
            if dim_name == player.dimension.name:
                for body_name, data in bodies.items():
                    if body_name.lower() == planet_name.lower():
                        planet_data = data
                        break
        
        if planet_data and "composition" in planet_data:
            print(f"Composition of {planet_name}:")
            for element, percentage in planet_data["composition"].items():
                print(f"  {element}: {percentage}%")
        else:
            print(f"Basic composition: Silicates, metals, and various minerals.")
            print("Detailed analysis unavailable - upgrade sensors for more information.")
        
        return True
    
    print(f"Unknown surface command: '{user_input}'. Type 'help' for available commands.")
    return True

def handle_move_command(player, direction):
    """Handle player movement and check for stations"""
    # ...existing movement code...
    
    # After movement, check if there's a station at these coordinates
    station = get_station_at_coords(player.x, player.y)
    if station:
        print(f"\nYou've discovered {station.name}!")
        dock = input("Would you like to dock? (y/n): ").strip().lower()
        if dock == "y" or dock == "yes":
            print(f"\nDocking at {station.name}...")
            player.docked_at = station
    
    # ...existing code...

def handle_scan_command(player):
    """Scan surroundings for points of interest"""
    # ...existing code...
    
    # Add nearby stations to scan results
    nearby_stations = []
    for station_id, station in STATIONS.items():
        # Prüfen, ob die Station in der gleichen Dimension ist
        if station.dimension == player.dimension.name:
            distance = ((station.x - player.x)**2 + (station.y - player.y)**2)**0.5
            if distance <= 10:  # Stations visible within 10 units
                nearby_stations.append((station, distance))
    
    if nearby_stations:
        print("\nStations detected:")
        for station, distance in sorted(nearby_stations, key=lambda x: x[1]):
            print(f"  {station.name} - Distance: {distance:.1f} units")
    
    # ...existing code...

def handle_dock_command(player, args):
    """Try to dock at a station"""
    # Check if player is already docked
    if player.docked_at:
        print(f"You are already docked at {player.docked_at.name}.")
        return
    
    # Check if there's a station at current coordinates
    station = get_station_at_coords(player.x, player.y)
    if station and station.dimension == player.dimension.name:
        print(f"\nDocking at {station.name}...")
        time.sleep(1)
        player.docked_at = station
    else:
        print("There is no station at your current location.")
        
        # Check if there are stations nearby
        nearby_stations = []
        for station_id, station in STATIONS.items():
            # Prüfen, ob die Station in der gleichen Dimension ist
            if station.dimension == player.dimension.name:
                distance = ((station.x - player.x)**2 + (station.y - player.y)**2)**0.5
                if distance <= 5:  # Stations within docking range
                    nearby_stations.append((station, distance))
        
        if nearby_stations:
            print("\nNearby stations detected:")
            for station, distance in sorted(nearby_stations, key=lambda x: x[1]):
                print(f"  {station.name} - Distance: {distance:.1f} units")
            print("\nNavigate to a station's coordinates to dock.")

def handle_land_command(player, body_name=None):
    """Land on a planet or moon if at the right coordinates"""
    # Player can't land if already landed
    if player.landed_on:
        print(f"You are already on the surface of {player.landed_on}.")
        return
    
    # Get current dimension's celestial bodies
    dimension_name = player.dimension.name
    bodies_in_dimension = {}
    
    # First check known bodies from player data
    if dimension_name in player.known_bodies:
        bodies_in_dimension = player.known_bodies[dimension_name]
    
    # If no bodies known yet, try to get them from dimension data
    if not bodies_in_dimension and hasattr(player.dimension, "properties"):
        bodies_in_dimension = player.dimension.properties
    
    # If we still don't have bodies, we can't land
    if not bodies_in_dimension:
        print("No celestial bodies detected in this area. Try scanning first.")
        return
    
    # If a specific body was provided, try to land on it
    if body_name:
        body_name = body_name.strip()
        target_body = None
        
        # Look for the requested body
        for name, data in bodies_in_dimension.items():
            if name.lower() == body_name.lower():
                target_body = (name, data)
                break
        
        if not target_body:
            print(f"Unknown celestial body: '{body_name}'.")
            return
        
        name, data = target_body
        
        # Check if player is at the body's coordinates
        if "coordinates" in data:
            body_x, body_y = data["coordinates"]
            if player.x != body_x or player.y != body_y:
                print(f"You must be at coordinates [{body_x}, {body_y}] to land on {name}.")
                return
            
        # Check if it's a landable body (not a star, gas giant, etc.)
        if "type" in data:
            body_type = data["type"].lower()
            if "star" in body_type or "sun" in body_type:
                print("WARNING: Cannot land on a star! That would be suicide.")
                return
            elif "gas" in body_type:
                print("Cannot land on a gas giant - there is no solid surface.")
                return
        
        # All checks passed, perform landing
        print(f"\nInitiating landing sequence on {name}...")
        for i in range(5, 0, -1):
            print(f"Landing in {i}...")
            time.sleep(0.5)
        
        print(f"\nLanded successfully on {name}.")
        player.landed_on = name
        return
    
    # If no body specified, check if player is at coordinates of any landable body
    potential_landing_sites = []
    
    for name, data in bodies_in_dimension.items():
        if "coordinates" in data:
            body_x, body_y = data["coordinates"]
            
            # Skip stars and gas giants
            if "type" in data:
                body_type = data["type"].lower()
                if "star" in body_type or "sun" in body_type or "gas" in body_type:
                    continue
            
            # Check coordinates
            if player.x == body_x and player.y == body_y:
                potential_landing_sites.append(name)
    
    if not potential_landing_sites:
        print("There are no landable celestial bodies at your current coordinates.")
        return
    
    if len(potential_landing_sites) == 1:
        # Only one option, land automatically
        body_name = potential_landing_sites[0]
        print(f"\nInitiating landing sequence on {body_name}...")
        for i in range(3, 0, -1):
            print(f"Landing in {i}...")
            time.sleep(0.5)
        
        print(f"\nLanded successfully on {body_name}.")
        player.landed_on = body_name
    else:
        # Multiple options, ask player to choose
        print("\nMultiple landing sites detected at current coordinates:")
        for i, name in enumerate(potential_landing_sites, 1):
            print(f"{i}. {name}")
        
        choice = input("\nSelect landing site (number) or 'cancel': ")
        
        if choice.lower() == 'cancel':
            print("Landing aborted.")
            return
        
        try:
            index = int(choice) - 1
            if 0 <= index < len(potential_landing_sites):
                body_name = potential_landing_sites[index]
                print(f"\nInitiating landing sequence on {body_name}...")
                for i in range(3, 0, -1):
                    print(f"Landing in {i}...")
                    time.sleep(0.5)
                
                print(f"\nLanded successfully on {body_name}.")
                player.landed_on = body_name
            else:
                print("Invalid selection. Landing aborted.")
        except ValueError:
            print("Invalid input. Landing aborted.")
