"""
System scanning functionality and celestial body detection.
"""
import time
import math
from src.config import DEFAULT_SCAN_RANGE, HIDDEN_SIGNALS, ANIMATION_SPEED

def scan_system(player):
    """Scan the current star system for celestial bodies"""
    # Get player position
    player_x = player.position("x")
    player_y = player.position("y")
    current_dimension = player.dimension
    dimension_name = current_dimension.name
    
    # Initialize list to store results
    scan_results = []
    
    # Check if this dimension is in known bodies dictionary
    if dimension_name not in player.known_bodies:
        player.known_bodies[dimension_name] = []
    
    # Scan all properties in the dimension
    for body_name, body_data in current_dimension.properties.items():
        # Extract coordinates and convert to integers
        body_x = int(body_data["Coordinates"]["x"])
        body_y = int(body_data["Coordinates"]["y"])
        
        # Calculate euclidean distance to player (for detection)
        distance = math.sqrt((player_x - body_x) ** 2 + (player_y - body_y) ** 2)
        
        # Calculate movement distance (Chebyshev distance - max of x,y differences)
        movement_distance = max(abs(player_x - body_x), abs(player_y - body_y))
        
        # Determine if body should be identified (if it's close enough or already known)
        # Using DEFAULT_SCAN_RANGE as the maximum identifiable distance
        if movement_distance <= DEFAULT_SCAN_RANGE or body_name in player.known_bodies.get(dimension_name, []):
            # Body is close enough to identify or already known
            body_type = body_data["type"]
            
            # Check if this is a new discovery
            is_new_discovery = False
            if dimension_name not in player.known_bodies or body_name not in player.known_bodies.get(dimension_name, []):
                is_new_discovery = True
                
            # Count signals (moons + stations)
            signals_count = 0
            
            # Count moons
            if "Moons" in body_data:
                if isinstance(body_data["Moons"], dict):
                    signals_count += len(body_data["Moons"])
                else:
                    signals_count += len(body_data["Moons"])
            
            # Count stations
            if "Stations" in body_data:
                signals_count += len(body_data["Stations"])
                
            result = {
                "name": body_name,
                "type": body_type,
                "coords": (body_x, body_y),
                "distance": movement_distance,
                "new_discovery": is_new_discovery,
                "signals_count": signals_count
            }
            
            # Add moons info if available
            if "Moons" in body_data:
                # Check if Moons is a dictionary (new format) or a list (old format)
                if isinstance(body_data["Moons"], dict):
                    result["moons"] = list(body_data["Moons"].keys())
                else:
                    result["moons"] = body_data["Moons"]
                
            scan_results.append(result)
        else:
            # Limited information for distant bodies (only coordinates are known)
            scan_results.append({
                "name": "Unknown",
                "type": "Unknown",
                "coords": (body_x, body_y),
                "distance": movement_distance,
                "new_discovery": False,
                "signals_count": 0
            })
    
    # Check for hidden signals in this dimension
    if dimension_name in HIDDEN_SIGNALS:
        for signal_name, coords in HIDDEN_SIGNALS[dimension_name].items():
            signal_x = coords["x"]
            signal_y = coords["y"]
            movement_distance = max(abs(player_x - signal_x), abs(player_y - signal_y))
            
            # Only show unknown signals when within scan range
            if movement_distance <= DEFAULT_SCAN_RANGE:
                # Always show as Unknown Signal with Anomaly type
                scan_results.append({
                    "name": "Unknown",
                    "type": "Unknown",
                    "coords": (signal_x, signal_y),
                    "distance": movement_distance,
                    "new_discovery": False,
                    "signals_count": 0
                })
    
    # Sort by distance to player
    scan_results.sort(key=lambda x: x["distance"])

    # Enhanced loading screen animation
    print("\nInitiating System Scan...\n")
    animation_chars = ["◓ ", "◑ ", "◒ ", "◐ "]
    scan_stages = [
        "Calibrating sensors   ",
        "Scanning for radiation",
        "Analyzing composition ",
        "Measuring mass        ",
        "Processing data       "
    ]
    
    line_length = 50  # Ensure this is long enough to overwrite previous lines
    
    for stage in scan_stages:
        for i in range(20):
            char = animation_chars[i % len(animation_chars)]
            progress = int((i+1)/20 * 10)
            bar = "█" * progress + "▒" * (10 - progress)
            status = f"{char}{stage} [{bar}] {min((i+1)*5, 100)}%"
            print(f"\r{status}{' ' * (line_length - len(status))}", end="", flush=True)
            time.sleep(ANIMATION_SPEED)
        print()  # Move to next line after stage completes
    
    print("\nScan complete! Processing results...\n")
    time.sleep(1)
    
    return scan_results

def handle_scan(player):
    """Process and display scan results"""
    try:
        # Get scan results
        raw_results = scan_system(player)
        
        # Filter results
        filtered_results = []
        for item in raw_results:
            # Skip moon objects
            if isinstance(item, dict) and 'type' in item and item['type'].lower() == 'moon':
                continue
                
            filtered_results.append((item, item['distance']))
        
        # Display results as a table
        if filtered_results:
            print("\n=== SCAN RESULTS ===")
            print(f"Found {len(filtered_results)} celestial bodies:")
            print(f"{'Type':<15} {'Name':<20} {'Coordinates':<20} {'Distance':<10} {'Signals':<10} {'Status':<10}")
            print("-" * 85)
            
            for obj_dict, distance in filtered_results:
                obj_name = obj_dict['name']
                obj_type = obj_dict.get('type', 'Unknown')
                coords = f"({obj_dict['coords'][0]}, {obj_dict['coords'][1]})"
                
                # Format distance as integer (travel time in seconds)
                distance_formatted = f"{int(distance)}s"
                
                # Get signals count (moons + stations)
                signals_count = obj_dict.get('signals_count', 0)
                
                # Set status based on whether it's a new discovery
                status = "NEW!" if obj_dict.get('new_discovery', False) else ""
                
                print(f"{obj_type:<15} {obj_name:<20} {coords:<20} {distance_formatted:<10} {signals_count:<10} {status:<10}")
            
            print("===================\n")
        else:
            print(f"\nNo objects detected in this system.")
        
        # Add discovered objects to player's knowledge
        current_dimension = player.position('dimension')
        for obj_dict, _ in filtered_results:
            # Only add named objects
            obj_name = obj_dict['name']
            if obj_name != 'Unknown':
                if current_dimension not in player.known_bodies:
                    player.known_bodies[current_dimension] = []
                if obj_name not in player.known_bodies[current_dimension]:
                    player.known_bodies[current_dimension].append(obj_name)
        
        return filtered_results
        
    except Exception as e:
        print(f"\nError during scan: {e}")
        return []

def scan_celestial_body(player, body_name):
    """Scan a specific celestial body for detailed information"""
    # Check if player's current dimension is known
    dim_name = player.dimension.name
    if dim_name not in player.known_dimensions:
        print(f"\n✗ Cannot scan {body_name}: This dimension is not fully mapped.")
        return
    
    # Check if we're trying to scan an "Unknown Signal" or "Anomaly"
    if body_name.lower() == "unknown signal" or body_name.lower() == "anomaly":
        # Check for nearby hidden signals
        player_x = player.position("x")
        player_y = player.position("y")
        signal_found = False
        
        if dim_name in HIDDEN_SIGNALS:
            for signal_name, coords in HIDDEN_SIGNALS[dim_name].items():
                signal_x = coords["x"]
                signal_y = coords["y"]
                distance = max(abs(player_x - signal_x), abs(player_y - signal_y))
                
                if distance <= DEFAULT_SCAN_RANGE:
                    signal_found = True
                    if distance <= 10:
                        print(f"\n=== DETAILED SCAN: {signal_name} ===")
                        print("Type: Special Signal")
                        print(f"Coordinates: [{signal_x}, {signal_y}]")
                        print("\nThis appears to be a significant discovery.")
                        print("==========================\n")
                        
                        # Add to known bodies
                        if dim_name not in player.known_bodies:
                            player.known_bodies[dim_name] = []
                        if signal_name not in player.known_bodies[dim_name]:
                            player.known_bodies[dim_name].append(signal_name)
                    else:
                        print(f"\n=== SCANNING UNKNOWN SIGNAL ===")
                        print("Signal detected but too weak for detailed analysis.")
                        print(f"Coordinates: [{signal_x}, {signal_y}]")
                        print("\nYou need to fly closer to properly analyze this signal.")
                        print("Try again when within 10 units of the coordinates.")
                        print("==========================\n")
                    break
        
        if not signal_found:
            print(f"\n✗ No unknown signals detected in range.")
        return
    
    # Check if trying to scan a hidden signal by name
    if dim_name in HIDDEN_SIGNALS and body_name in HIDDEN_SIGNALS[dim_name]:
        player_x = player.position("x")
        player_y = player.position("y")
        signal_x = HIDDEN_SIGNALS[dim_name][body_name]["x"]
        signal_y = HIDDEN_SIGNALS[dim_name][body_name]["y"]
        distance = max(abs(player_x - signal_x), abs(player_y - signal_y))
        
        # For hidden signals, always show the error message regardless of distance
        print(f"\n✗ Cannot scan {body_name}: Signal not strong enough.")
        print("   You need a much more powerful direct scanning tool.")
        return
    
    # First check if it's a main celestial body
    body_data = None
    is_moon = False
    parent_planet = None
    
    # Look for the body as a primary celestial object
    for name, data in player.dimension.properties.items():
        if name.lower() == body_name.lower():
            body_data = data
            body_name = name  # Use the correct case from the data
            break
    
    # If not found as a primary body, check if it's a moon
    if not body_data:
        for planet_name, planet_data in player.dimension.properties.items():
            if 'Moons' in planet_data and planet_name in player.known_bodies.get(dim_name, []):
                # Only search for moons of planets that are already known
                for moon_name, moon_data in planet_data['Moons'].items():
                    if moon_name.lower() == body_name.lower():
                        body_data = moon_data
                        body_name = moon_name  # Use the correct case
                        is_moon = True
                        parent_planet = planet_name
                        break
                if is_moon:
                    break

    # If not found, or if it's a moon of an unknown planet, prevent scanning
    if not body_data:
        print(f"\n✗ Cannot scan {body_name}: Object not found in this system.")
        return
    elif is_moon and parent_planet not in player.known_bodies.get(dim_name, []):
        print(f"\n✗ Cannot scan {body_name}: You need to discover its parent planet first.")
        print("   Perform a system scan to discover the parent planet.")
        return
    
    # For primary bodies (non-moons), check if they are known or a star
    if not is_moon:
        is_known = False
        is_star = body_data.get("type", "").lower() == "star"
        
        # Stars are always considered known
        if is_star:
            is_known = True
        elif dim_name in player.known_bodies and body_name in player.known_bodies[dim_name]:
            is_known = True
            
        if not is_known:
            print(f"\n✗ Cannot scan {body_name}: You haven't discovered this celestial body yet.")
            print("   Perform a system scan first to discover new bodies.")
            return
    
    # Print detailed scan results
    print(f"\n=== DETAILED SCAN: {body_name} ===")
    
    # Print body type if available
    if 'type' in body_data:
        print(f"Type: {body_data['type']}")
    elif is_moon:
        print(f"Type: Moon of {parent_planet}")
    
    # Print coordinates if available
    if 'Coordinates' in body_data:
        try:
            x = body_data['Coordinates']['x']
            y = body_data['Coordinates']['y']
            print(f"Coordinates: [{x}, {y}]")
        except KeyError:
            pass
    
    # If this is a planet, list its moons
    if not is_moon and 'Moons' in body_data and body_data['Moons']:
        print("\n--- Moons ({}) ---".format(len(body_data['Moons'])))
        print(f"{'Name'.ljust(15)}{'Coordinates'.ljust(15)}")
        print("-" * 30)
        
        for moon_name, moon_data in body_data['Moons'].items():
            # Get moon coordinates
            moon_coords = "[Unknown]"
            if 'Coordinates' in moon_data:
                try:
                    moon_x = moon_data['Coordinates']['x']
                    moon_y = moon_data['Coordinates']['y']
                    moon_coords = f"[{moon_x}, {moon_y}]"
                except KeyError:
                    pass
            
            print(f"{moon_name.ljust(15)}{moon_coords.ljust(15)}")
    
    # Show stations/structures
    stations_count = 0
    stations_info = []
    
    # Get stations information
    if 'Stations' in body_data:
        for station_name, station_data in body_data['Stations'].items():
            stations_count += 1
            station_type = station_data.get('type', 'Unknown')
            
            # Get station coordinates
            station_coords = "[Unknown]"
            if 'Coordinates' in station_data:
                station_x = station_data['Coordinates']['x']
                station_y = station_data['Coordinates']['y']
                station_coords = f"[{station_x}, {station_y}]"
            
            station_desc = station_data.get('description', 'No description available')
            stations_info.append((station_name, station_type, station_coords, station_desc))
    
    # Display stations information if any found
    if stations_count > 0:
        print(f"\n--- Stations/Structures ({stations_count}) ---")
        print(f"{'Name'.ljust(15)}{'Type'.ljust(10)}{'Coordinates'.ljust(15)}{'Description'}")
        print("-" * 70)
        
        for name, typ, coords, desc in stations_info:
            print(f"{name.ljust(15)}{typ.ljust(10)}{coords.ljust(15)}{desc}")
    
    # Add celestial body to player's known bodies - maintaining the list format for compatibility
    if dim_name not in player.known_bodies:
        player.known_bodies[dim_name] = []
        
    # Only add primary bodies (not moons) to the known bodies list
    if not is_moon:
        # Add the body to the list if not already present
        if body_name not in player.known_bodies[dim_name]:
            player.known_bodies[dim_name].append(body_name)
    
    print("==========================\n")