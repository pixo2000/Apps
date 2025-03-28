"""
UI display functions for the Spacer game.
"""
import time
import random
from src.config import LOADING_BAR_LENGTH, GAME_TITLE, ANIMATION_SPEED

def display_loading_animation():
    """Display an animated loading screen at game start"""
    # Calculate padding to center the title
    console_width = 80  # Assumed console width
    title_padding = (console_width - len(GAME_TITLE)) // 2
    title_display = " " * title_padding + GAME_TITLE
    
    print("\n" + "=" * console_width)
    print(title_display)
    print("=" * console_width + "\n")

    # Loading animation
    print("Initializing systems...")
    time.sleep(0.5)
    
    # Show loading bar
    for i in range(101):
        bar_filled = int((i / 100) * LOADING_BAR_LENGTH)
        bar_empty = LOADING_BAR_LENGTH - bar_filled
        
        # Create the loading bar with blocks
        bar = '█' * bar_filled + '▒' * bar_empty
        
        # Print the loading bar with percentage
        print(f"\rLoading: [{bar}] {i}%", end="", flush=True)
        time.sleep(ANIMATION_SPEED * random.uniform(0.1, 0.5))
    
    print("\n\nAll systems online.\n")

def display_help(first_time=False):
    """Display help information for the player"""
    if first_time:
        print("\n=== WELCOME TO SPACER ===")
        print("An interstellar exploration game")
        print("\nYou are a captain of a small spacecraft, free to explore the cosmos.")
        print("Use commands to navigate between star systems and discover celestial bodies.")
    else:
        print("\n=== SPACER HELP ===")
    
    # Get commands from registry if available
    try:
        from src.commands.registry import CommandRegistry
        import importlib
        registry_module = importlib.import_module("src.commands.command_manager")
        if hasattr(registry_module, "command_registry"):
            registry = registry_module.command_registry
            
            # Group commands by type
            navigation_commands = []
            scan_commands = []
            interaction_commands = []
            player_commands = []
            system_commands = []
            
            for cmd_name, cmd in registry.commands.items():
                if cmd_name in ["move", "jump", "whereami", "dimensions"]:
                    navigation_commands.append(cmd)
                elif cmd_name in ["scan", "scancoords"]:
                    scan_commands.append(cmd)
                elif cmd_name in ["dock", "land", "launch", "trade", "repair", "quests"]:
                    interaction_commands.append(cmd)
                elif cmd_name in ["playerinfo", "changename", "discoveries", "self-destruct"]:
                    player_commands.append(cmd)
                else:
                    system_commands.append(cmd)
            
            # Display commands by group
            if navigation_commands:
                print("\nNavigation Commands:")
                for cmd in navigation_commands:
                    print(f"  {cmd.name.ljust(12)} - {cmd.description}")
                
            if scan_commands:
                print("\nScanning Commands:")
                for cmd in scan_commands:
                    print(f"  {cmd.name.ljust(12)} - {cmd.description}")
                
            if interaction_commands:
                print("\nInteraction Commands:")
                for cmd in interaction_commands:
                    print(f"  {cmd.name.ljust(12)} - {cmd.description}")
                
            if player_commands:
                print("\nPlayer Commands:")
                for cmd in player_commands:
                    print(f"  {cmd.name.ljust(12)} - {cmd.description}")
                
            if system_commands:
                print("\nSystem Commands:")
                for cmd in system_commands:
                    print(f"  {cmd.name.ljust(12)} - {cmd.description}")
                    
            print("\nFor more information on specific commands, check the command documentation.")
            print("====================\n")
            return
    except (ImportError, AttributeError):
        pass
    
    # Fallback to static command list if registry not available
    print("\nBasic Commands:")
    print("  scan        - Scan current system for celestial bodies")
    print("  move X Y    - Move to coordinates [X, Y]")
    print("  jump DIM    - Jump to dimension DIM (e.g., 'jump A01')")
    print("  whereami    - Show current location")
    print("  dimensions  - List available dimensions")
    print("  dock        - Dock at a station (when at station coordinates)")
    print("  land        - Land on a planet (when at city coordinates)")
    
    print("\nInfo Commands:")
    print("  playerinfo  - Show your information")
    print("  discoveries - List your discoveries")
    
    print("\nSystem Commands:")
    print("  help        - Show this help message")
    print("  logout      - Save and return to login screen")
    print("  exit/quit   - Save and exit game")
    
    print("\nFor more information, visit the Spacer documentation.")
    print("====================\n")

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
        
        # Show current location if not dead - REMOVED to preserve privacy
        # Instead, only show dimension they are in without exact coordinates
        if not is_dead:
            # Get dimension name only
            pos = save_data.get('position', {})
            dim_name = pos.get('dimension', 'Unknown')
            
            # Try to get dimension title
            try:
                from src.world.dimension import Dimension
                dim = Dimension(dim_name)
                dim_title = dim.title
                print(f"» Current system: {dim_name} ({dim_title})")
            except:
                print(f"» Current system: {dim_name}")
            
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
            
        # Show playtime if available
        if 'playtime' in save_data:
            print(f"» Total playtime: {save_data['playtime']}")
            
        print("===========================\n")
    else:
        print(f"\n✗ No captain found with the name '{player_name}'")
