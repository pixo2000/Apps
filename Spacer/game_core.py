"""
Core game initialization and main loop functionality.
"""
import time
import os
import datetime
from player import Player
from save_manager import SaveManager
from ui_display import display_help, display_loading_animation
from command_handler import handle_input

# Global save manager instance
save_mgr = SaveManager()

def initialize_game():
    """Initialize the game and show welcome screen"""
    display_loading_animation()
    print("\nSystem initialized. Ready for commands.\n")
    
    # Check for existing save files
    saved_players = save_mgr.get_all_players()
    all_players = save_mgr.get_all_players_including_dead()
    
    if saved_players:
        print("Saved captains found:")
        for i, saved_name in enumerate(saved_players, 1):
            print(f"{i}. {saved_name}")
        
        while True:
            choice = input("\nEnter captain name to continue, 'new' for new game, or 'exit' to quit: ")
            
            if choice.lower() == 'new':
                return create_new_captain()
            elif choice.lower() == 'exit':
                print("\nExiting game. Goodbye!")
                exit(0)
            
            # Check if player exists but is dead
            if any(name.lower() == choice.lower() for name in all_players):
                if save_mgr.is_player_dead(choice):
                    print(f"\n☠ Captain {choice} is deceased. Their journey has ended.")
                    print("  Choose another captain or start a new game.")
                    continue
            
            # Case-insensitive player name check for living captains
            for saved_name in saved_players:
                if saved_name.lower() == choice.lower():
                    return saved_name, True, False  # Return exact name, load_save flag, show_tutorial flag
            
            print("Captain not found. Please try again.")
    else:
        return create_new_captain()

def create_new_captain():
    """Handle creation of a new captain with name validation"""
    while True:
        name = input("Who are you, Captain? (or 'exit' to quit): ")
        
        if name.lower() == 'exit':
            print("\nExiting game. Goodbye!")
            exit(0)
            
        # Check name validity
        if not save_mgr.is_valid_player_name(name):
            print("\n⚠ Invalid name. Names must be 3-15 characters long and can contain:")
            print("  - Uppercase letters (A-Z)")
            print("  - Lowercase letters (a-z)")
            print("  - Numbers (0-9)")
            print("  - Underscores (_)")
            
            if name.lower() in save_mgr.reserved_names:
                print("\n⚠ Additionally, this name is reserved as a system command and cannot be used.")
            continue
            
        # Check if name already exists
        if save_mgr.player_exists(name):
            if save_mgr.is_player_dead(name):
                print(f"\n⚠ A captain named {name} has perished. Choose another name")
                print("  to honor their memory.")
            else:
                print(f"\n⚠ A captain named {name} already exists. Choose another name.")
            continue
            
        # Valid new name
        print("\n" + "*" * 50)
        print(f"Welcome aboard, Captain {name}!")
        print("Your journey through the cosmos begins now.")
        print("*" * 50 + "\n")
        time.sleep(1)
        
        return name, False, True  # New captain, don't load save, show tutorial

def update_playtime(player_obj, session_start):
    """Update player's total playtime by adding the current session time"""
    try:
        session_end = datetime.datetime.now()
        session_duration = (session_end - session_start).total_seconds()
        
        if hasattr(player_obj, "playtime"):
            player_obj.playtime += session_duration
        else:
            player_obj.playtime = session_duration
            
        save_mgr.save_game(player_obj)
    except Exception as e:
        print(f"Error updating playtime: {e}")

def main_game_loop():
    """Main game loop that handles player sessions"""
    while True:
        try:
            # Get player name and flags
            result = initialize_game()
            if len(result) == 3:
                name, load_save, show_help = result
            else:
                name, load_save = result
                show_help = not load_save
                
            player = Player(name)
            
            # Load saved game if requested
            if load_save:
                save_data = save_mgr.load_game(name)
                if player.load_save_data(save_data):
                    print(f"\nWelcome back, Captain {name}!")
                    print(f"Resuming from {player.dimension.title}, coordinates [{player.x}, {player.y}]")
                    
                    # Parse playtime from save data
                    if "playtime" in save_data:
                        playtime_str = save_data["playtime"]
                        player.playtime = save_mgr.parse_playtime(playtime_str)
                    else:
                        player.playtime = 0
                    
                    # Load creation date and last login from save
                    if "creation_date" in save_data:
                        player.creation_date = save_data["creation_date"]
                else:
                    print("\nError loading save. Starting new game.")
                    show_help = True
                    player.playtime = 0
                    player.creation_date = datetime.datetime.now().isoformat()
            else:
                # New player
                player.playtime = 0
                player.creation_date = datetime.datetime.now().isoformat()
            
            # Record session start time
            session_start = datetime.datetime.now()
            player.session_start = session_start
            
            # Show help menu for new players
            if show_help:
                display_help(first_time=True)
            
            running = True
            
            while running:
                check = handle_input(player)
                if check == "negative":
                    # Exit game entirely
                    running = False
                    update_playtime(player, session_start)
                    return
                elif check == "logout":
                    # Return to login screen
                    running = False
                    update_playtime(player, session_start)
                    print("\nReturning to login screen...\n")
                    time.sleep(1)
                    os.system("clear")
        
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            print("\n\nEmergency shutdown initiated. Saving game...")
            update_playtime(player, session_start)
            if save_mgr.save_game(player):
                print("Game saved successfully. Goodbye!")
            else:
                print("Warning: Game could not be saved.")
            break
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            print("Game will restart...")
            time.sleep(2)

def run_game(debug):
    if debug == "true":
        print("Not clearing console because debug is set to true")

        main_game_loop()

    else:
        # Clear the screen
        os.system('cls' if os.name == 'nt' else 'clear')
        
        main_game_loop()

if __name__ == "__main__":
    run_game()
