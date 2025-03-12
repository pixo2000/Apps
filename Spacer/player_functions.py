import math
import tqdm
import time

def scan_system(player):
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
        
        # Calculate distance to player
        distance = math.sqrt((player_x - body_x) ** 2 + (player_y - body_y) ** 2)
        
        # Determine if body should be identified
        if distance <= 250 or body_name in player.known_bodies[dimension_name]:
            # Body is close enough to identify or already known
            body_type = body_data["type"]
            
            # Mark as discovered
            if body_name not in player.known_bodies[dimension_name]:
                player.known_bodies[dimension_name].append(body_name)
                is_new_discovery = True
            else:
                is_new_discovery = False
                
            result = {
                "name": body_name,
                "type": body_type,
                "coords": (body_x, body_y),
                "distance": distance,
                "new_discovery": is_new_discovery
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
            # Limited information for distant bodies
            scan_results.append({
                "name": "Unknown",
                "type": "Unknown",
                "coords": (body_x, body_y),
                "distance": distance,
                "new_discovery": False
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
            time.sleep(0.1)
        print()  # Move to next line after stage completes
    
    print("\nScan complete! Processing results...\n")
    time.sleep(1)
    
    return scan_results

def display_scan_results(scan_results):
    print("\n=== SCAN RESULTS ===")
    print(f"Found {len(scan_results)} celestial bodies:")
    
    # Header for table format
    print(f"{'Type':<15} {'Name':<20} {'Coordinates':<20} {'Distance':<10} {'Status':<10}")
    print("-" * 75)
    
    for body in scan_results:
        # Format distance to show only 2 decimal places
        distance_formatted = f"{body['distance']:.2f}"
        
        # Show discovery status
        status = "NEW!" if body.get("new_discovery", False) else ""
        
        print(f"{body['type']:<15} {body['name']:<20} {str(body['coords']):<20} {distance_formatted:<10} {status:<10}")
        
        # Show moons if present and body is known
        if body['name'] != "Unknown" and "moons" in body:
            moon_list = ", ".join(body["moons"])
            print(f"   └─ Moons: {moon_list}")
    
    print("===================\n")
