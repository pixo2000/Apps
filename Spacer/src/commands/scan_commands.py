"""
Scanner command handlers for celestial body detection.
"""
import time
import math
from src.world.scanner import handle_scan, scan_celestial_body
from src.world.station import STATIONS, check_coords_for_objects

def handle_scan_command(player):
    """Handle the scan command to scan the current system"""
    handle_scan(player)

def handle_specific_scan_command(player, body_name):
    """Handle scanning a specific celestial body"""
    scan_celestial_body(player, body_name)

def handle_simple_scan(player):
    """Scan surroundings for points of interest (simplified version of scanner)"""
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
            
            # Check if this body is already known to the player
            is_known = False
            if dim_name in player.known_bodies and body_name in player.known_bodies[dim_name]:
                is_known = True
                
            # For stars, they are always detectable regardless of discovery
            is_star = body_data.get("type", "").lower() == "star"
            
            # Only show details for known bodies or stars, otherwise show as "Unknown"
            if distance <= 10:  # Detect bodies within 10 units
                if is_known or is_star:
                    nearby_bodies.append((body_name, body_data["type"], distance))
                else:
                    # For unknown bodies, show only limited information
                    nearby_bodies.append(("Unknown Object", "Unknown", distance))
    
    # Display results
    if nearby_bodies:
        print("\nDetected celestial bodies:")
        for name, body_type, dist in sorted(nearby_bodies, key=lambda x: x[2]):
            print(f"  {name} ({body_type}) - Distance: {dist} units")
    else:
        print("\nNo significant celestial bodies detected nearby.")

def handle_coordinate_scan(player, coords):
    """
    Handle scanning specific coordinates from a station
    Only works when player is docked at a station or landed
    """
    # Parse coordinates
    try:
        parts = coords.split()
        if len(parts) != 2:
            raise ValueError("Requires exactly two numbers")
        
        x = int(parts[0])
        y = int(parts[1])
    except ValueError:
        print("\n✗ Invalid coordinates format. Please use: scancoords <x> <y>")
        print("  Example: scancoords 50 -30")
        return
    
    # Perform the scan
    print(f"\nInitiating long-range scan of coordinates [{x}, {y}]...")
    
    # Add a small animation for scanning
    animation_chars = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
    for i in range(10):
        print(f"\r{animation_chars[i % len(animation_chars)]} Focusing scanning array... {'▰' * (i+1)}{'▱' * (9-i)} {(i+1)*10}%", end="", flush=True)
        time.sleep(0.15)
    print()  # New line after animation
    
    # Get the result from the coordinates check
    result = check_coords_for_objects(x, y, player.dimension.name, {"bodies": player.dimension.properties})
    
    # Process and display the results
    if result["found"]:
        print(f"\n=== SCAN RESULTS FOR [{x}, {y}] ===")
        for obj in result["objects"]:
            if "parent" in obj:
                print(f"Detected: {obj['name']} ({obj['type']} of {obj['parent']})")
            else:
                print(f"Detected: {obj['name']} ({obj['type']})")
                
            if "description" in obj:
                print(f"Details: {obj['description']}")
            print()
            
            # Add to player's discovered objects if not already known
            obj_name = obj["name"]
            dim_name = player.dimension.name
            
            if dim_name not in player.known_bodies:
                player.known_bodies[dim_name] = []
                
            if obj_name not in player.known_bodies[dim_name]:
                player.known_bodies[dim_name].append(obj_name)
                print(f"» New discovery added to log: {obj_name}")
                
        print("===================================")
    else:
        print(f"\nScan complete. No objects detected at coordinates [{x}, {y}].")
        print("The area appears to be empty space.")
