"""
Navigation functions for the Spacer game.
Handles movement and dimension jumping.
"""
import time
from src.world.dimension import Dimension
from src.core.save_manager import SaveManager
from src.world.station import load_stations_from_dimension

# Create save manager instance
save_mgr = SaveManager()

def perform_move(player, x, y):
    """
    Move player to the specified coordinates
    
    Args:
        player: The player object
        x (int): X-coordinate to move to
        y (int): Y-coordinate to move to
        
    Returns:
        bool: True if move was successful
    """
    # Check if destination is inside a star before moving
    if is_inside_star(player, x, y):
        # Show warning and ask for confirmation
        print(f"\n⚠️  WARNING: Destination [{x}, {y}] appears to be inside a star!")
        print("Proceeding with this navigation will result in the destruction of your ship.")
        
        # Ask for confirmation
        confirm = input("\nDo you want to proceed anyway? (y/n): ").strip().lower()
        if confirm != 'y':
            print("\nNavigation aborted. Staying at current position.")
            return False
            
        # Player confirmed - start movement animation even though it will end in death
        print(f"\nNavigating to coordinates [{x}, {y}]...")
        
        # Animate movement with a progress bar
        distance = max(abs(player.x - x), abs(player.y - y))
        for i in range(distance):
            progress = int((i+1)/distance * 20)
            bar = "█" * progress + "▒" * (20 - progress)
            print(f"\r[{bar}] {i+1}/{distance} units traveled", end="", flush=True)
            time.sleep(0.1)
        
        # Player has arrived at the star and is now dead
        print(f"\nYou've reached coordinates [{x}, {y}]")
        print("\n⚠️ CRITICAL ERROR: Temperature exceeding safe limits!")
        print("\n☠️ Your ship has been incinerated by intense stellar radiation.")
        print("\nYou are dead. Type 'restart' to begin a new game.")
        
        # Set player position and death status
        player.x = x
        player.y = y
        player.is_dead = True
        
        # Save the game with player's dead status
        save_mgr.save_game(player)
        return True
        
    # Calculate distance (which is also movement time)
    distance = max(abs(player.x - x), abs(player.y - y))
    
    # Start movement
    print(f"\nNavigating to coordinates [{x}, {y}]...")
    
    # Animate movement with a progress bar
    for i in range(distance):
        progress = int((i+1)/distance * 20)
        bar = "█" * progress + "▒" * (20 - progress)
        print(f"\r[{bar}] {i+1}/{distance} units traveled", end="", flush=True)
        time.sleep(0.1)
    
    print(f"\nArrived at coordinates [{x}, {y}]")
    
    # Update player position
    player.x = x
    player.y = y
    
    # Check for special locations
    check_location(player)
    
    return True

def is_inside_star(player, dest_x, dest_y):
    """
    Check if the destination coordinates are inside a star
    
    Args:
        player: The player object
        dest_x (int): Destination X-coordinate
        dest_y (int): Destination Y-coordinate
        
    Returns:
        bool: True if destination is inside a star
    """
    if not player.dimension:
        return False
        
    dimension = player.dimension
    
    # Check all bodies in the dimension
    for body_name, body_data in dimension.properties.items():
        # Only check stars
        if body_data.get("type", "").lower() == "star" and "Coordinates" in body_data and "size" in body_data:
            try:
                star_x = int(body_data["Coordinates"]["x"])
                star_y = int(body_data["Coordinates"]["y"])
                
                # Get the star's boundaries directly from size
                # The size represents how far the star extends in each direction from its center
                star_width = int(body_data["size"]["width"])
                star_height = int(body_data["size"]["height"])
                
                # Check if destination is within the star's boundaries
                # If dest_x is between (star_x - star_width) and (star_x + star_width)
                # AND dest_y is between (star_y - star_height) and (star_y + star_height)
                if (star_x - star_width <= dest_x <= star_x + star_width and 
                    star_y - star_height <= dest_y <= star_y + star_height):
                    return True
            except (ValueError, KeyError):
                # Skip if we can't parse the coordinates or size properly
                continue
                
    return False

def perform_jump(player, dimension_name):
    """
    Jump to another dimension
    
    Args:
        player: The player object
        dimension_name (str): Name of the dimension to jump to
        
    Returns:
        bool: True if jump was successful, False otherwise
    """
    # Check if dimension exists
    try:
        new_dimension = Dimension(dimension_name)
    except Exception as e:
        print(f"\n✗ Jump failed: {str(e)}")
        return False
    
    # Perform the jump with animation
    print(f"\nInitiating jump to {dimension_name} ({new_dimension.title})...")
    
    # Jump animation
    animation_frames = ["◓ ", "◑ ", "◒ ", "◐ "]
    for i in range(10):
        char = animation_frames[i % len(animation_frames)]
        progress = int((i+1)/10 * 20)
        bar = "█" * progress + "▒" * (20 - progress)
        status = f"{char}Jump in progress [{bar}] {(i+1)*10}%"
        print(f"\r{status}", end="", flush=True)
        time.sleep(0.2)
    print()  # New line after animation
    
    # Set new dimension
    old_dimension = player.dimension.name
    player.dimension = new_dimension
    
    # Set spawn coordinates to [10, 10] in the new dimension
    player.x = 10
    player.y = 10
    
    # Add to known dimensions
    if dimension_name not in player.known_dimensions:
        player.known_dimensions.append(dimension_name)
    
    # Clear screen and show message
    print(f"\nJump complete! Welcome to {new_dimension.title}.")
    
    # Load stations for this dimension
    load_stations_from_dimension({'bodies': new_dimension.properties}, dimension_name)
    
    # Check location after jump
    check_location(player)
    
    # Save the game after a jump
    save_mgr.save_game(player)
    return True

def check_location(player):
    """Check if player is at any special location and show information"""
    dimension = player.dimension
    
    # Check for celestial bodies at current location
    for body_name, body_data in dimension.properties.items():
        if "Coordinates" in body_data:
            body_x = int(body_data["Coordinates"]["x"])
            body_y = int(body_data["Coordinates"]["y"])
            if body_x == player.x and body_y == player.y:
                # Check if this is a new discovery
                is_new = False
                if dimension.name not in player.known_bodies:
                    player.known_bodies[dimension.name] = []
                if body_name not in player.known_bodies[dimension.name]:
                    player.known_bodies[dimension.name].append(body_name)
                    is_new = True
                
                # Print discovery message
                if is_new:
                    print(f"\n» You've discovered {body_name}!")
                else:
                    print(f"\n» You've reached {body_name}.")
                
                # Show basic info if it's a star
                if body_data.get("type", "").lower() == "star":
                    print(f"Type: {body_data['type']}")
                    if "description" in body_data:
                        print(f"Description: {body_data['description']}")
                break
