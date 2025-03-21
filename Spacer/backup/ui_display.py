"""
User interface components and display functions.
"""
import time
import json
import datetime
from pathlib import Path
from dimension import Dimension
from save_manager import SaveManager

# Create save manager instance for formatting helpers
save_mgr = SaveManager()

def display_loading_animation():
    """Display an animation for game initialization"""
    print("\n" + "=" * 50)
    print(" " * 12 + "SPACER - EXPLORE AND DIE")
    print("=" * 50 + "\n")
    
    # Animation for initialization
    loading_messages = ["Initializing systems", "Calibrating navigation", "Loading universe"]
    max_length = max(len(message) for message in loading_messages) + 4  # +4 for the "..." and some padding
    
    for message in loading_messages:
        print(f"\r{message}...{' ' * (max_length - len(message) - 3)}", end="", flush=True)
        time.sleep(0.8)
    print("\r" + " " * max_length)  # Properly clear the line after all messages

def display_help(first_time=False):
    """Display the help menu with available commands"""
    if first_time:
        print("\n" + "=" * 60)
        print("     WELCOME TO SPACER - INTERSTELLAR EXPLORATION SYSTEM")
        print("=" * 60)
        print("\nYou are the captain of a spacecraft exploring the cosmos.")
        print("Your journey begins in the SOL system, our own solar system.")
        print("\nHere are the basic commands to get you started:\n")
    else:
        print("\n" + "=" * 40)
        print("      SPACER - AVAILABLE COMMANDS")
        print("=" * 40)
    
    print("\n== NAVIGATION ==")
    print("  move X Y       - Move to coordinates X,Y")
    print("  jump SYSTEM    - Jump to another star system (e.g., jump A01)")
    print("  dimensions     - List all known and unknown star systems")
    print("  whereami       - Display current position information")
    
    print("\n== INTERACTION ==")
    print("  scan           - Scan the surrounding area for celestial bodies")
    print("  scan NAME      - Scan a specific celestial body in detail")
    print("  dock           - Dock at a station (when at station coordinates)")
    print("  land           - Land on a planet or moon (when at celestial body coordinates)")
    print("  land NAME      - Land on a specific planet or moon (must be at its coordinates)")
    
    print("\n== CHARACTER ==")
    print("  playerinfo     - Display information about your character")
    print("  changename NAME - Change your captain's name")
    print("  discoveries    - List all your discovered celestial bodies")
    
    print("\n== SYSTEM ==")
    print("  help           - Show this help message")
    print("  logout         - Save game and return to login screen")
    print("  exit/quit      - Save game and exit")
    
    print("\n== CONTEXT SPECIFIC COMMANDS ==")
    print("  When docked at a station or landed on a planet,")
    print("  different commands will be available. Type 'help' in")
    print("  these contexts to see the available options.")
    
    if first_time:
        print("\nStart by exploring your surrounding area with the 'scan' command.")
        print("Good luck, Captain!\n")

def display_discoveries(player):
    """Display all discoveries made by the player"""
    print("\n" + "=" * 50)
    print("             YOUR DISCOVERIES")
    print("=" * 50)
    
    print(f"\nDimensions visited: {len(player.known_dimensions)}")
    for dim_name in player.known_dimensions:
        try:
            dim = Dimension(dim_name)
            bodies_count = len(player.known_bodies.get(dim_name, []))
            print(f"\n» {dim_name}: {dim.title}")
            print(f"  {dim.description}")
            print(f"  Discovered bodies: {bodies_count}")
            
            if bodies_count > 0:
                for body in player.known_bodies[dim_name]:
                    print(f"   - {body}")
        except:
            print(f"» {dim_name}: [Data corrupted]")
    
    print("\n" + "=" * 50)

def display_other_player_info(player_name):
    """Display information about another player by name"""
    print("\n=== PLAYER INFORMATION ===")
    
    # Get player data from save files
    player_data = None
    for save_file in save_mgr.save_directory.glob('*.json'):
        try:
            with open(save_file, 'r') as f:
                data = json.load(f)
                if data.get("name", "").lower() == player_name.lower():
                    player_data = data
                    break
        except:
            continue
    
    if not player_data:
        print(f"» Captain '{player_name}' not found in records.")
        print("=========================\n")
        return
        
    print(f"» Name: {player_data['name']}")
    
    # Show UUID
    if "uuid" in player_data:
        print(f"» UUID: {player_data['uuid']}")
    
    # Show status (alive/deceased)
    status = "Alive" if not player_data.get("is_dead", False) else "Deceased"
    print(f"» Status: {status}")
    
    # Only show discovery stats if player is not dead
    if not player_data.get("is_dead", False):
        # Show discoveries stats
        try:
            dims_visited = len(player_data["discoveries"]["known_dimensions"])
            print(f"» Dimensions visited: {dims_visited}")
        except:
            print("» Dimensions visited: Unknown")
        
        # Count total bodies
        try:
            known_bodies = player_data["discoveries"]["known_bodies"]
            total_bodies = sum(len(bodies) for bodies in known_bodies.values())
            print(f"» Celestial bodies discovered: {total_bodies}")
        except:
            print("» Celestial bodies discovered: Unknown")
        
        # Show playtime if available in save file
        if "playtime" in player_data:
            # Display the formatted playtime string directly from the save file
            playtime = player_data["playtime"]
            print(f"» Total playtime: {playtime}")
        
        # Show creation date and last login
        if "creation_date" in player_data:
            creation_date = save_mgr.format_date(player_data["creation_date"])
            print(f"» Created: {creation_date}")
        
        if "last_login" in player_data:
            last_login = save_mgr.format_date(player_data["last_login"])
            print(f"» Last login: {last_login}")
    
    print("=========================\n")
