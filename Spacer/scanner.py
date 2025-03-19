"""
System scanning functionality and celestial body detection.
"""
import math
import time
from config import DEFAULT_SCAN_RANGE, HIDDEN_SIGNALS, ANIMATION_SPEED

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
            
            # Only include if player is very close to the hidden signal
            if movement_distance <= 10:  # Much shorter detection range for hidden signals
                is_new_discovery = signal_name not in player.known_bodies.get(dimension_name, [])
                
                scan_results.append({
                    "name": signal_name,
                    "type": "Special Signal",
                    "coords": (signal_x, signal_y),
                    "distance": movement_distance,
                    "new_discovery": is_new_discovery,
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
    """Scan a specific celestial body for moons and stations"""
    try:
        current_dimension = player.dimension
        
        # Check if the player knows this dimension
        dim_name = current_dimension.name
        if dim_name not in player.known_dimensions:
            print(f"\n✗ Cannot scan {body_name}: This dimension is not fully mapped.")
            return
        
        # Look for the body in the current dimension
        body_data = None
        for name, data in current_dimension.properties.items():
            if name.lower() == body_name.lower():
                body_data = data
                body_name = name  # Use the correct case from the data
                break
        
        if not body_data:
            print(f"\n✗ Cannot scan {body_name}: Object not found in this system.")
            return
        
        # Check if the body is in the player's known bodies list
        if body_name not in player.known_bodies.get(dim_name, []):
            print(f"\n✗ Cannot scan {body_name}: Object not in database. Perform a system scan first.")
            return
        
        # Basic body info
        body_type = body_data.get("type", "Unknown")
        body_x = body_data["Coordinates"]["x"]
        body_y = body_data["Coordinates"]["y"]
        
        print(f"\n=== DETAILED SCAN: {body_name} ===")
        print(f"Type: {body_type}")
        print(f"Coordinates: [{body_x}, {body_y}]")
        
        # Scan for moons
        if "Moons" in body_data and body_data["Moons"]:
            print(f"\n--- Moons ({len(body_data['Moons'])}) ---")
            print(f"{'Name':<15} {'Coordinates':<15}")
            print("-" * 30)
            
            for moon_name, moon_data in body_data["Moons"].items():
                moon_x = moon_data["Coordinates"]["x"]
                moon_y = moon_data["Coordinates"]["y"]
                print(f"{moon_name:<15} [{moon_x}, {moon_y}]")
        
        # Scan for stations
        if "Stations" in body_data and body_data["Stations"]:
            print(f"\n--- Stations/Structures ({len(body_data['Stations'])}) ---")
            print(f"{'Name':<15} {'Type':<10} {'Coordinates':<15} {'Description'}")
            print("-" * 70)
            
            for station_name, station_data in body_data["Stations"].items():
                station_type = station_data.get("type", "Unknown")
                station_x = station_data["Coordinates"]["x"] if "Coordinates" in station_data else "N/A"
                station_y = station_data["Coordinates"]["y"] if "Coordinates" in station_data else "N/A"
                desc = station_data.get("description", "")
                
                # Format coordinates
                coords = f"[{station_x}, {station_y}]" if station_x != "N/A" else "N/A"
                
                print(f"{station_name:<15} {station_type:<10} {coords:<15} {desc}")
        
        # If no moons or stations were found
        if ("Moons" not in body_data or not body_data["Moons"]) and \
           ("Stations" not in body_data or not body_data["Stations"]):
            print("\nNo satellites or structures detected.")
        
        print("==========================\n")
        
    except Exception as e:
        print(f"\nScan error: {e}")
