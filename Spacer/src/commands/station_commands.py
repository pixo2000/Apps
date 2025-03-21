"""
Station and landing interaction command handlers.
"""
import time
from src.world.station import get_station_at_coords, get_city_at_coords
from src.core.save_manager import SaveManager

# Create save manager instance for saving after docking/landing
save_mgr = SaveManager()

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
        
        # Save the game after successful docking
        save_mgr.save_game(player)
        print(f"Welcome to {station.name}!")
    else:
        print("There is no station at your current location.")
        
        # Check if there are stations nearby
        nearby_stations = []
        from src.world.station import STATIONS
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

def handle_station_input(player):
    """Handle input while docked at a station"""
    # Display station options only once when first docking
    if not hasattr(player, "_station_options_shown") or player._station_options_shown != player.docked_at.name:
        player.docked_at.display_options()
        player._station_options_shown = player.docked_at.name
    
    user_input = input(f"\n[{player.docked_at.name}] {player.name}> ").strip().lower()
    
    if user_input == "exit" or user_input == "quit":
        # Save before quitting
        save_mgr.save_game(player)
        print("\n=== SYSTEM SHUTDOWN ===")
        print("Saving station status... Done!")
        print("Closing connections...")
        print("\nGoodbye Captain! Safe travels.\n")
        return "negative"
    
    if user_input == "logout":
        print("\n=== LOGGING OUT ===")
        print(f"Saving current session at {player.docked_at.name}...")
        save_mgr.save_game(player)
        print("Station status and session data saved successfully.")
        print("Returning to login screen...")
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
        landing_location = f"{city.name} on {parent_moon} (Moon of {parent_body})"
    else:
        landing_location = f"{city.name} on {parent_body}"
    
    print(f"\nLanded successfully at {landing_location}.")
    
    # Store both the city name, parent moon (if applicable) and parent body
    player.landed_on = city.name
    player.landed_on_body = parent_body
    if parent_moon:
        player.landed_on_moon = parent_moon
    
    # Save the game after successful landing
    save_mgr.save_game(player)
    return

def handle_planet_input(player):
    """Handle input while landed on a planet or moon"""
    city_name = player.landed_on
    body_name = getattr(player, "landed_on_body", "Unknown Body")
    moon_name = getattr(player, "landed_on_moon", None)
    
    display_location = body_name
    if moon_name:
        display_location = f"{moon_name} (Moon of {body_name})"
    
    # Display options only once when first landing
    if not hasattr(player, "_city_options_shown") or player._city_options_shown != city_name:
        print(f"\n== {city_name} on {display_location} ==")
        print("Available commands:")
        print("  explore    - Explore the surroundings")
        print("  launch     - Return to orbit")
        print("  analyze    - Analyze surface composition")
        print("  info       - Show detailed information about this location")
        print("  help       - Show this help message")
        print("  logout     - Save and return to login screen")
        print("  exit/quit  - Save and exit game")
        player._city_options_shown = city_name
    
    user_input = input(f"\n[{city_name}] {player.name}> ").strip().lower()
    
    if user_input == "exit" or user_input == "quit":
        # Save before quitting
        save_mgr.save_game(player)
        print("\n=== SYSTEM SHUTDOWN ===")
        print(f"Saving surface status on {city_name}... Done!")
        print("Closing connections...")
        print("\nGoodbye Captain! Safe travels.\n")
        return "negative"
    
    if user_input == "logout":
        print("\n=== LOGGING OUT ===")
        print(f"Saving current session on {city_name}...")
        save_mgr.save_game(player)
        print("Surface status and session data saved successfully.")
        print("Returning to login screen...")
        return "logout"
    
    if user_input == "help":
        # Show planet-specific help
        print("\n== Surface Operations Help ==")
        print(f"You are currently on {city_name} on the surface of {display_location}. Available commands:")
        print("  explore    - Explore the surroundings for resources and discoveries")
        print("  launch     - Return to orbit and resume space travel")
        print("  analyze    - Perform detailed analysis of surface composition")
        print("  info       - Show detailed information about this location")
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
        
        # Get planet/moon data from the dimension properties directly
        body_data = None
        
        if moon_name:
            # If on a moon, look for the moon data in its parent planet
            for b_name, data in player.dimension.properties.items():
                if b_name == body_name and "Moons" in data:
                    for m_name, m_data in data["Moons"].items():
                        if m_name == moon_name:
                            body_data = m_data
                            break
                    if body_data:  # Break outer loop if found
                        break
        else:
            # If on a planet, look for the planet data directly
            for b_name, data in player.dimension.properties.items():
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
    
    elif user_input == "info":
        print(f"\n== {city_name} on {display_location} Information ==")
        
        # Get planet/moon data directly from the dimension properties
        body_data = None
        
        if moon_name:
            # If on a moon, look for the moon data in its parent planet
            for b_name, data in player.dimension.properties.items():
                if b_name == body_name and "Moons" in data:
                    for m_name, m_data in data["Moons"].items():
                        if m_name == moon_name:
                            body_data = m_data
                            break
                    if body_data:  # Break outer loop if found
                        break
        else:
            # If on a planet, look for the planet data directly
            for b_name, data in player.dimension.properties.items():
                if b_name == body_name:
                    body_data = data
                    break
        
        # Display information about the location
        loc_type = "Moon" if moon_name else "Planet"
        if body_data and "type" in body_data:
            loc_type = body_data["type"]
        
        print(f"Type: {loc_type}")
        
        # Show coordinates
        coords = "Unknown"
        if body_data and "Coordinates" in body_data:
            x = body_data["Coordinates"]["x"]
            y = body_data["Coordinates"]["y"]
            coords = f"[{x}, {y}]"
        print(f"Coordinates: {coords}")
        
        # Show dimension info
        print(f"Dimension: {player.dimension.name} - {player.dimension.title}")
        
        # Show parent info for moons
        if moon_name:
            print(f"Parent Body: {body_name}")
        
        # Show composition if available
        if body_data and "composition" in body_data:
            print("\nComposition:")
            for element, percentage in body_data["composition"].items():
                print(f"  {element}: {percentage}%")
        
        # Show stations/cities on this body
        if body_data and "Stations" in body_data:
            print("\nStations/Cities:")
            for station_name, station_data in body_data["Stations"].items():
                s_type = station_data.get("type", "Unknown")
                s_desc = station_data.get("description", "No description available")
                s_coords = "Unknown"
                if "Coordinates" in station_data:
                    s_x = station_data["Coordinates"]["x"]
                    s_y = station_data["Coordinates"]["y"]
                    s_coords = f"[{s_x}, {s_y}]"
                print(f"  {station_name} ({s_type}) - {s_coords}")
                print(f"  Description: {s_desc}")
        
        # Show additional description if available
        if body_data and "description" in body_data:
            print(f"\nDescription: {body_data['description']}")
        
        return True
    
    print(f"Unknown surface command: '{user_input}'. Type 'help' for available commands.")
    return True
