"""
Scanner command handlers for celestial body detection.
"""
import time
from src.world.scanner import handle_scan, scan_celestial_body
from src.world.station import check_coords_for_objects
from src.config import HIDDEN_SIGNALS

def handle_scan_command(player):
    """Handle the scan command to scan the current system"""
    handle_scan(player)

def handle_specific_scan_command(player, body_name):
    """Handle scanning a specific celestial body"""
    scan_celestial_body(player, body_name)

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
            if "parent" in obj and "grandparent" in obj:
                print(f"Detected: {obj['name']} ({obj['type']} on {obj['parent']}, Moon of {obj['grandparent']})")
            elif "parent" in obj:
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
