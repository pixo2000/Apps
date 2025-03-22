"""
Navigation and movement command handlers.
"""
import time
from src.world.dimension import Dimension
from src.config import MOVEMENT_SPEED, WARP_PATHS
from src.world.station import load_stations_from_dimension

def move(player, x, y):
    """Move the player to specified coordinates"""
    # Calculate the distance (maximum of x or y difference for diagonal movement)
    distance = max(abs(x - player.x), abs(y - player.y))
    
    if distance == 0:
        print("\n✓ Already at the requested coordinates.\n")
        return
        
    print(f"\n➤ Setting course to coordinates [{x}, {y}]")
    
    # Show countdown and wait for each field
    for remaining in range(distance, 0, -1):
        progress = distance - remaining
        bar_length = 30
        
        # Calculate percentage for positioning
        percent = (progress / distance) * 100
        
        # For the final step (approaching 100%), ensure the ship is at the very end
        if remaining == 1:
            ship_position = bar_length - 1  # Place at the very end for final step
        else:
            # Otherwise calculate normal position
            ship_position = int((progress / distance) * bar_length)
        
        # Ensure ship position is within valid range
        ship_position = min(max(0, ship_position), bar_length - 1)
        
        # Create the spacebar with the ship at the correct position
        spacebar = "·" * ship_position + "🚀" + "·" * (bar_length - ship_position - 1)
        
        # Calculate percentage (fixed to avoid showing multiple percentages)
        if remaining == 1:
            display_percent = 100  # Always show 100% for the final step
        else:
            display_percent = int(percent)
        
        # Add extra buffer space to ensure previous output is completely overwritten
        buffer_space = " " * 40
        
        # Display improved movement animation with spaceship
        print(f"\r[{spacebar}] Moving... {remaining} second{'s' if remaining != 1 else ''} remaining [{display_percent}%]{buffer_space}", end="", flush=True)
        time.sleep(MOVEMENT_SPEED)
        
        # After waiting for the regular countdown, show final approach message for the last step
        if remaining == 1:
            print(f"\r[{spacebar}] Moving... Final approach [{display_percent}%]{buffer_space}", end="", flush=True)
            time.sleep(0.2)  # Add extra wait for final approach
            
    # Update position
    player.x = x
    player.y = y
    print(f"\n\n✓ Arrived at coordinates [{x}, {y}]\n")

def handle_move_command(player, x, y):
    """Handle player movement and check for stations"""
    move(player, x, y)
    
    # After movement, check if there's a station at these coordinates
    from src.world.station import get_station_at_coords
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
                break

def handle_jump_command(player, dimension_name):
    """Jump to a different dimension"""
    try:
        current_dimension = player.dimension.name
        
        # Check if player is trying to jump to the current dimension
        if dimension_name == current_dimension:
            print(f"\n✗ JUMP FAILED: You are already in the {dimension_name} system.")
            return
            
        # Check if current dimension exists in WARP_PATHS
        if current_dimension not in WARP_PATHS:
            print(f"\n✗ JUMP FAILED: No warp paths available from {current_dimension}.")
            return
        
        # Check if target dimension is in the allowed warp paths
        if dimension_name not in WARP_PATHS[current_dimension]:
            print(f"\n✗ JUMP FAILED: Cannot warp directly from {current_dimension} to {dimension_name}.")
            print(f"  Available warp destinations from {current_dimension}: {', '.join(WARP_PATHS[current_dimension])}")
            return
            
        new_dimension = Dimension(dimension_name)
        print(f"\n▼ DIMENSIONAL JUMP SEQUENCE INITIATED ▼")
        print(f"➤ Target: {new_dimension.title}")
        print(f"➤ Preparing and calibrating jump engines...")
        
        # Replace tqdm with custom loading bar
        total_steps = 100
        bar_width = 40
        
        for step in range(total_steps + 1):
            # Calculate progress
            progress = step / total_steps
            bar_filled = int(bar_width * progress)
            bar_empty = bar_width - bar_filled
            
            # Create loading bar with customized appearance
            bar = '█' * bar_filled + '▒' * bar_empty
            percent = int(progress * 100)
            
            # Print loading bar with "Charging" prefix
            print(f"\rCharging [" + bar + f"] {percent}%", end="", flush=True)
            time.sleep(0.1)
        print()  # Line break after loading completes

        print(f"\n➤ Jump sequence activated! Entering hyperspace...")
        time.sleep(1)
        
        # Animation for the jump
        jump_animation = ["■□□□□", "□■□□□", "□□■□□", "□□□■□", "□□□□■", "□□□■□", "□□■□□", "□■□□□"]
        for _ in range(3):  # 3 cycles of animation
            for frame in jump_animation:
                print(f"\r▻▻▻ {frame} ◅◅◅", end="", flush=True)
                time.sleep(0.1)
        
        # Update player state
        player.dimension = new_dimension
        player.x = 10
        player.y = 10
        
        # Add dimension to known dimensions if not already there
        if dimension_name not in player.known_dimensions:
            player.known_dimensions.append(dimension_name)
        
        print(f"\n\n✓ JUMP COMPLETE")
        print(f"\n== Welcome to {new_dimension.title} ==")
        print(f"» {new_dimension.description}")
        print(f"» Starting coordinates: [10, 10]\n")
        
        # Load stations from the new dimension
        load_stations_from_dimension({'bodies': new_dimension.properties}, dimension_name)
        
    except ValueError as e:
        print(f"\n✗ JUMP FAILED: {str(e)}\n")

def handle_whereami_command(player):
    """Display the player's current location information"""
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
