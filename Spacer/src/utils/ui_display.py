"""
UI display functions for the Spacer game.
"""
import time
import random
from src.config import LOADING_BAR_LENGTH, GAME_TITLE, ANIMATION_SPEED

def display_loading_animation():
    """Display an animated loading screen at game start"""
    print("\n" + "=" * 50)
    print(f"{GAME_TITLE:^50}")
    print("=" * 50 + "\n")

    print("Initializing systems...")

    # Display animated loading bar
    for i in range(101):
        progress = i / 100
        bar = "█" * int(LOADING_BAR_LENGTH * progress) + "▒" * (LOADING_BAR_LENGTH - int(LOADING_BAR_LENGTH * progress))
        print(f"\r[{bar}] {i}%", end="", flush=True)
        time.sleep(ANIMATION_SPEED / 3)  # Faster than normal animations

    print("\n\nSystems online.")

def display_help(first_time=False):
    """Display available commands and help information"""
    if first_time:
        print("\n" + "=" * 50)
        print("WELCOME TO SPACER - COMMAND REFERENCE".center(50))
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("COMMAND REFERENCE".center(50))
        print("=" * 50)

    print("\n== NAVIGATION ==")
    print("  move X Y    - Move to coordinates [X, Y]")
    print("  whereami    - Display current location")
    print("  dimensions  - List available dimensions")
    print("  jump DIM    - Jump to dimension (e.g. 'jump A01')")
    
    print("\n== SCANNING ==")
    print("  scan              - Scan current system")
    print("  scan [BODY NAME]  - Get detailed info about celestial body")
    
    print("\n== STATION INTERACTIONS ==")
    print("  dock       - Dock at station (must be at station coordinates)")
    print("  land       - Land on planet with city (must be at city coordinates)")
    
    print("\n== PLAYER COMMANDS ==")
    print("  playerinfo       - Show your information")
    print("  playerinfo NAME  - Show info about another captain")
    print("  discoveries      - List your discoveries")
    print("  changename NAME  - Change your captain name")
    
    print("\n== SYSTEM COMMANDS ==")
    print("  help      - Show this help")
    print("  logout    - Return to login screen")
    print("  exit/quit - Exit game")
    
    print("\nExplore the cosmos, discover new dimensions, and chart your own path!")
    print("=" * 50 + "\n")

def display_discoveries(player):
    """Display player's discoveries"""
    print("\n=== DISCOVERIES LOG ===")
    
    # Show dimensions discovered
    print(f"Dimensions explored: {len(player.known_dimensions)}")
    for dimension in sorted(player.known_dimensions):
        print(f"  » {dimension}")
    
    # Show celestial bodies discovered, organized by dimension
    if hasattr(player, 'known_bodies') and player.known_bodies:
        print("\nCelestial bodies discovered:")
        total_bodies = 0
        
        for dimension, bodies in player.known_bodies.items():
            if bodies:  # Only show dimensions with discoveries
                total_bodies += len(bodies)
                bodies_list = sorted(bodies)  # Sort alphabetically
                
                # Try to get dimension title if available
                try:
                    from src.world.dimension import Dimension
                    dim_obj = Dimension(dimension)
                    dim_title = f"{dimension} - {dim_obj.title}"
                except:
                    dim_title = dimension
                
                print(f"  » {dim_title}: {len(bodies)}")
                
                # Display each celestial body, checking for moon notation (parent:moon)
                planets = []
                moons = {}
                
                for body in bodies_list:
                    if ":" in body:
                        parent, moon = body.split(":", 1)
                        if parent not in moons:
                            moons[parent] = []
                        moons[parent].append(moon)
                    else:
                        planets.append(body)
                
                # Display planets first
                for planet in planets:
                    print(f"    • {planet}")
                    # If this planet has moons, list them indented
                    if planet in moons:
                        for moon in moons[planet]:
                            print(f"      - {moon}")
        
        print(f"\nTotal celestial bodies discovered: {total_bodies}")
    else:
        print("\nNo celestial bodies have been discovered yet.")
        
    print("=======================\n")

def display_other_player_info(player_name):
    """Display information about another player"""
    from src.core.save_manager import SaveManager
    save_mgr = SaveManager()
    
    # Try to load the other player's data
    save_data = save_mgr.load_game(player_name)
    
    if save_data:
        # Player found, show their information
        print("\n=== CAPTAIN INFORMATION ===")
        print(f"» Name: {save_data['name']}")
        
        # Show status
        is_dead = save_data.get('is_dead', False)
        status = 'Deceased' if is_dead else 'Active'
        print(f"» Status: {status}")
        
        # Show current location if not dead
        if not is_dead:
            # Get dimension name and position
            pos = save_data.get('position', {})
            dim_name = pos.get('dimension', 'Unknown')
            x = pos.get('x', '?')
            y = pos.get('y', '?')
            
            # Try to get dimension title
            try:
                from src.world.dimension import Dimension
                dim = Dimension(dim_name)
                dim_title = dim.title
            except:
                dim_title = "Unknown System"
                
            print(f"» Current location: {dim_name} ({dim_title}) at [{x}, {y}]")
            
            # Show docked or landed status if applicable
            if save_data.get('docked_at'):
                print(f"» Currently docked at a station")
            elif save_data.get('landed_on'):
                landed_location = save_data.get('landed_on', 'Unknown')
                landed_body = save_data.get('landed_on_body', 'Unknown')
                print(f"» Currently landed at {landed_location} on {landed_body}")
        
        # Show creation date if available
        if 'creation_date' in save_data:
            from src.core.save_manager import SaveManager
            save_mgr = SaveManager()
            creation_date = save_mgr.format_date(save_data['creation_date'])
            print(f"» Created: {creation_date}")
            
        # Show last login if available
        if 'last_login' in save_data:
            print(f"» Last seen: {save_data['last_login']}")
            
        # Show dimensions discovered count
        if 'discoveries' in save_data and 'known_dimensions' in save_data['discoveries']:
            dims_count = len(save_data['discoveries']['known_dimensions'])
            print(f"» Dimensions visited: {dims_count}")
            
        # Show celestial bodies discovered count
        if 'discoveries' in save_data and 'known_bodies' in save_data['discoveries']:
            known_bodies = save_data['discoveries']['known_bodies']
            total_count = sum(len(bodies) for bodies in known_bodies.values())
            print(f"» Celestial bodies discovered: {total_count}")
            
        print("===========================\n")
    else:
        print(f"\n✗ No captain found with the name '{player_name}'")
