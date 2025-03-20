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
from station import STATIONS, get_station_at_coords, get_city_at_coords, load_stations_from_dimension

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
        
        # Load stations from the new dimension
        if hasattr(player, 'dimension') and player.dimension:
            load_stations_from_dimension({'bodies': player.dimension.properties}, player.dimension.name)
        
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
    
    user_input = input(f"\n[{player.docked_at.name}] {player.name}> ").strip().lower()
    
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
    city_name = player.landed_on
    body_name = getattr(player, "landed_on_body", "Unknown Body")
    moon_name = getattr(player, "landed_on_moon", None)
    
    display_location = body_name
    if moon_name:
        display_location = f"{moon_name} (moon of {body_name})"
    
    # Display options only once when first landing
    if not hasattr(player, "_city_options_shown") or player._city_options_shown != city_name:
        print(f"\n== {city_name} on {display_location} ==")
        print("Available commands:")
        print("  explore    - Explore the surroundings")
        print("  launch     - Return to orbit")
        print("  analyze    - Analyze surface composition")
        print("  help       - Show this help message")
        print("  logout     - Save and return to login screen")
        print("  exit/quit  - Save and exit game")
        player._city_options_shown = city_name
    
    user_input = input(f"\n[{city_name}] {player.name}> ").strip().lower()
    
    if user_input == "exit" or user_input == "quit":
        return "negative"
    
    if user_input == "logout":
        return "logout"
    
    if user_input == "help":
        # Show planet-specific help
        print("\n== Surface Operations Help ==")
        print(f"You are currently on {city_name} on the surface of {display_location}. Available commands:")
        print("  explore    - Explore the surroundings for resources and discoveries")
        print("  launch     - Return to orbit and resume space travel")
        print("  analyze    - Perform detailed analysis of surface composition")
        print("\nGeneral commands:")
        print("  help       - Show this help message")
        print("  logout     - Save and return to login screen")
        print("  exit/quit  - Save and exit game")
        return True
    
    elif user_input == "launch":
        print(f"\nLaunching from {city_name} on {display_location}...")
        time.sleep(1)
        player.landed_on = None
        player.landed_on_body = None
        if hasattr(player, "landed_on_moon"):
            player.landed_on_moon = None
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
        
        # Adjust the location display based on whether it's a moon or planet
        location_display = display_location
        
        # Get planet/moon data from player's known bodies if available
        body_data = None
        for dim_name, bodies in player.known_bodies.items():
            if dim_name == player.dimension.name:
                # If it's a moon, we need to check the moon data specifically
                if moon_name:
                    for b_name, data in bodies.items():
                        if b_name == body_name and "Moons" in data:
                            if moon_name in data["Moons"]:
                                body_data = data["Moons"][moon_name]
                                break
                else:
                    # Direct planet search
                    for b_name, data in bodies.items():
                        if b_name == body_name:
                            body_data = data
                            break
        
        if body_data and "composition" in body_data:
            print(f"Composition of {location_display}:")
            for element, percentage in body_data["composition"].items():
                print(f"  {element}: {percentage}%")
        else:
            print(f"Basic composition: Silicates, metals, and various minerals.")
            print("Detailed analysis unavailable - upgrade sensors for more information.")
        
        return True
    
    print(f"Unknown surface command: '{user_input}'. Type 'help' for available commands.")
    return True

def handle_move_command(player, direction):
    """Handle player movement and check for stations"""
    # Get current position
    current_x = player.x
    current_y = player.y
    
    # Calculate new position based on direction
    new_x, new_y = current_x, current_y
    if direction == "north":
        new_y -= 1
    elif direction == "south":
        new_y += 1
    elif direction == "east":
        new_x += 1
    elif direction == "west":
        new_x -= 1
    
    # Update player position
    player.x = new_x
    player.y = new_y
    print(f"Moved to coordinates [{new_x}, {new_y}]")
    
    # After movement, check if there's a station at these coordinates
    station = get_station_at_coords(player.x, player.y, player.dimension.name)
    if station:
        print(f"\nYou've discovered {station.name}!")
        dock = input("Would you like to dock? (y/n): ").strip().lower()
        if dock == "y" or dock == "yes":
            print(f"\nDocking at {station.name}...")
            player.docked_at = station
    
    # Check for planets or other points of interest
    for body_name, body_data in player.dimension.properties.items():
        if "Coordinates" in body_data:
            body_x = int(body_data["Coordinates"]["x"])
            body_y = int(body_data["Coordinates"]["y"])
            if body_x == player.x and body_y == player.y:
                print(f"\nYou've reached {body_name}!")
                # Additional logic for interacting with the celestial body can be added here
                break

def handle_scan_command(player):
    """Scan surroundings for points of interest"""
    print("\nScanning surrounding space...")
    time.sleep(1)
    
    # Get player position
    player_x = player.x
    player_y = player.y
    dim_name = player.dimension.name
    
    # Find nearby celestial bodies
    nearby_bodies = []
    for body_name, body_data in player.dimension.properties.items():
        if "Coordinates" in body_data:
            body_x = int(body_data["Coordinates"]["x"])
            body_y = int(body_data["Coordinates"]["y"])
            distance = max(abs(player_x - body_x), abs(player_y - body_y))
            if distance <= 10:  # Detect bodies within 10 units
                nearby_bodies.append((body_name, body_data["type"], distance))
    
    # Add nearby stations to scan results
    nearby_stations = []
    for station_id, station in STATIONS.items():
        # Check if the station is in the same dimension
        if station.dimension == player.dimension.name:
            distance = ((station.x - player.x)**2 + (station.y - player.y)**2)**0.5
            if distance <= 10:  # Stations visible within 10 units
                nearby_stations.append((station, distance))
    
    if nearby_stations:
        print("\nStations detected:")
        for station, distance in sorted(nearby_stations, key=lambda x: x[1]):
            print(f"  {station.name} ({station.type}) - Distance: {distance:.1f} units")
    
    # Display results
    if nearby_bodies:
        print("\nDetected celestial bodies:")
        for name, body_type, dist in sorted(nearby_bodies, key=lambda x: x[2]):
            print(f"  {name} ({body_type}) - Distance: {dist} units")
    else:
        print("\nNo significant celestial bodies detected nearby.")

def handle_dock_command(player):
    """Try to dock at a station"""
    # Check if player is already docked
    if player.docked_at:
        print(f"You are already docked at {player.docked_at.name}.")
        return
    
    # Check if there's a station at current coordinates
    station = get_station_at_coords(player.x, player.y, player.dimension.name)
    if station:
        print(f"\nDocking at {station.name}...")
        time.sleep(1)
        player.docked_at = station
    else:
        print("There is no station at your current location.")
        
        # Check if there are stations nearby
        nearby_stations = []
        from station import STATIONS
        for station_id, station in STATIONS.items():
            # Check if the station is in the same dimension
            if station.dimension == player.dimension.name and station.type in ["Station", "Beacon"]:
                distance = ((station.x - player.x)**2 + (station.y - player.y)**2)**0.5
                if distance <= 5:  # Stations within docking range
                    nearby_stations.append((station, distance))
        
        if nearby_stations:
            print("\nNearby stations detected:")
            for station, distance in sorted(nearby_stations, key=lambda x: x[1]):
                print(f"  {station.name} - Distance: {distance:.1f} units")
            print("\nNavigate to a station's coordinates to dock.")

def handle_land_command(player, body_name=None):
    """Land on a planet or moon if at the right coordinates and there's a city there"""
    # Player can't land if already landed
    if player.landed_on:
        print(f"You are already on the surface of {player.landed_on}.")
        return
    
    # Check if there's a city at current coordinates
    city = get_city_at_coords(player.x, player.y, player.dimension.name)
    
    if not city:
        print("There is no city or landing site at your current coordinates.")
        return
    
    # Get the celestial body name for the city
    parent_body = None
    parent_moon = None
    
    # Use the stored parent_moon and parent_body if available
    if hasattr(city, 'parent_moon') and city.parent_moon:
        parent_moon = city.parent_moon
        parent_body = city.parent_body
    else:
        # Legacy fallback - search through the dimension data
        for body_name, body_data in player.dimension.properties.items():
            # Check stations directly on the body
            if 'Stations' in body_data:
                for station_name, station_data in body_data['Stations'].items():
                    if station_name == city.name:
                        parent_body = body_name
                        break
            
            # Check if it's on a moon
            if not parent_body and 'Moons' in body_data:
                for moon_name, moon_data in body_data['Moons'].items():
                    if 'Stations' in moon_data:
                        for station_name, station_data in moon_data['Stations'].items():
                            if station_name == city.name:
                                parent_body = body_name  # This is the planet
                                parent_moon = moon_name  # This is the moon
                                break
                    if parent_moon:
                        break
            
            if parent_body:
                break
    
    if not parent_body:
        # If we couldn't determine the body name, use the city name as fallback
        parent_body = "Unknown Body"
    
    # All checks passed, perform landing
    print(f"\nInitiating landing sequence on {parent_moon or parent_body}, {city.name}...")
    for i in range(3, 0, -1):
        print(f"Landing in {i}...")
        time.sleep(0.5)
    
    landing_location = f"{city.name}"
    if parent_moon:
        landing_location = f"{city.name} on {parent_moon} (moon of {parent_body})"
    else:
        landing_location = f"{city.name} on {parent_body}"
    
    print(f"\nLanded successfully at {landing_location}.")
    
    # Store both the city name, parent moon (if applicable) and parent body
    player.landed_on = city.name
    player.landed_on_body = parent_body
    if parent_moon:
        player.landed_on_moon = parent_moon
    return
