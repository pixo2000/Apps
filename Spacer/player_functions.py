import math
import tqdm
import time

def scan_system(player):
    # Get player position
    player_x = player.position("x")
    player_y = player.position("y")
    current_dimension = player.dimension
    
    # Initialize list to store results
    scan_results = []
    
    # Scan all properties in the dimension
    for body_name, body_data in current_dimension.properties.items():
        # Extract coordinates and convert to integers
        body_x = int(body_data["Coordinates"]["x"])
        body_y = int(body_data["Coordinates"]["y"])
        
        # Calculate distance to player
        distance = math.sqrt((player_x - body_x) ** 2 + (player_y - body_y) ** 2)
        
        if distance <= 250:
            # Full information for nearby bodies
            body_type = body_data["type"]
            scan_results.append({
                "name": body_name,
                "type": body_type,
                "coords": (body_x, body_y),
                "distance": distance
            })
        else:
            # Limited information for distant bodies
            scan_results.append({
                "name": "Unknown",
                "type": "Unknown",
                "coords": (body_x, body_y),
                "distance": distance
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
    print(f"{'Type':<15} {'Name':<20} {'Coordinates':<20} {'Distance':<10}")
    print("-" * 65)
    
    for body in scan_results:
        # Format distance to show only 2 decimal places
        distance_formatted = f"{body['distance']:.2f}"
        print(f"{body['type']:<15} {body['name']:<20} {str(body['coords']):<20} {distance_formatted:<10}")
    
    print("===================\n")
