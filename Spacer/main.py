# import other files
import player
import player_input as pinput
from save_manager import SaveManager

# import modules
import time
import os
import datetime  # Added for date/time tracking

# load stuff
def temp_start():
#    os.system("clear") # clear console, works on codespace but not on windows
    print("\n" + "=" * 50)
    print("  SPACER - INTERSTELLAR EXPLORATION SIMULATOR")
    print("=" * 50 + "\n")
    
    # Animation für die Initialisierung
    loading_messages = ["Initializing systems", "Calibrating navigation", "Loading universe"]
    max_length = max(len(message) for message in loading_messages) + 4  # +4 for the "..." and some padding
    
    for message in loading_messages:
        print(f"\r{message}...{' ' * (max_length - len(message) - 3)}", end="", flush=True)
        time.sleep(0.8)
    print("\r" + " " * max_length)  # Properly clear the line after all messages
    
    print("\nSystem initialized. Ready for commands.\n")
    
    # Check for existing save files
    save_mgr = SaveManager()
    saved_players = save_mgr.get_all_players()
    all_players = save_mgr.get_all_players_including_dead()
    
    if saved_players:
        print("Saved captains found:")
        for i, saved_name in enumerate(saved_players, 1):
            print(f"{i}. {saved_name}")
        
        while True:
            choice = input("\nEnter captain name to continue, 'new' for new game, or 'exit' to quit: ")
            
            if choice.lower() == 'new':
                return create_new_captain(save_mgr)
            elif choice.lower() == 'exit':
                print("\nExiting game. Goodbye!")
                exit(0)  # Exit the program immediately
            
            # First check if the player name exists but is dead
            if any(name.lower() == choice.lower() for name in all_players):
                # Player exists (might be dead), check status
                if save_mgr.is_player_dead(choice):
                    print(f"\n☠ Captain {choice} is deceased. Their journey has ended.")
                    print("  Choose another captain or start a new game.")
                    continue
                
            # Case-insensitive player name check for living captains
            for saved_name in saved_players:
                if saved_name.lower() == choice.lower():
                    return saved_name, True, False  # Return exact name, load_save flag, show_tutorial flag
            
            # If we reach here, the player wasn't found at all
            print("Captain not found. Please try again.")
    else:
        return create_new_captain(save_mgr)

def create_new_captain(save_mgr):
    """Handle creation of a new captain with name validation"""
    while True:
        name = input("Who are you, Captain? (or 'exit' to quit): ")
        
        if name.lower() == 'exit':
            print("\nExiting game. Goodbye!")
            exit(0)  # Exit the program immediately
            
        # Check length and allowed characters
        if not save_mgr.is_valid_player_name(name):
            print("\n⚠ Invalid name. Names must be 3-15 characters long and can contain:")
            print("  - Uppercase letters (A-Z)")
            print("  - Lowercase letters (a-z)")
            print("  - Numbers (0-9)")
            print("  - Underscores (_)")
            
            # Check specifically for reserved names
            if name.lower() in save_mgr.reserved_names:
                print("\n⚠ Additionally, this name is reserved as a system command and cannot be used.")
            
            continue
            
        # Check if name already exists (case insensitive)
        if save_mgr.player_exists(name):
            # Check if existing player is dead
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
        
        # The player object will be created with a creation date
        # No need to use metadata anymore as everything is stored in the UUID-based save file
        
        return name, False, True  # New captain, don't load save, show tutorial

# main loop
def main():
    # Loop to handle logout and new login
    while True:
        try:
            # Get player name and flags
            result = temp_start()
            if len(result) == 3:  # Updated to handle 3 values
                name, load_save, show_help = result
            else:
                name, load_save = result
                show_help = not load_save  # Show help for new players
                
            me = player.Player(name)
            
            # Update last login time and load player data
            save_mgr = SaveManager()
            
            # Load saved game if requested
            if load_save:
                save_data = save_mgr.load_game(name)
                if me.load_save_data(save_data):
                    print(f"\nWelcome back, Captain {name}!")
                    print(f"Resuming from {me.dimension.title}, coordinates [{me.x}, {me.y}]")
                    
                    # Parse playtime from save data
                    if "playtime" in save_data:
                        playtime_str = save_data["playtime"]
                        me.playtime = save_mgr.parse_playtime(playtime_str)
                    else:
                        me.playtime = 0
                    
                    # Load creation date and last login from save if available
                    if "creation_date" in save_data:
                        me.creation_date = save_data["creation_date"]
                else:
                    print("\nError loading save. Starting new game.")
                    show_help = True  # Show help if load failed
                    me.playtime = 0  # Initialize playtime to 0 for new game
                    me.creation_date = datetime.datetime.now().isoformat()  # Set creation date for new game
            else:
                # New player, initialize playtime to 0 and set creation date
                me.playtime = 0
                me.creation_date = datetime.datetime.now().isoformat()
            
            # Record session start time on both a variable and the player object
            session_start = datetime.datetime.now()
            me.session_start = session_start
            
            # Show help menu for new players
            if show_help:
                pinput.display_help(first_time=True)
            
            running = True
            
            while running:
                check = pinput.handle_input(me)
                if check == "negative":
                    # Exit the game entirely
                    running = False
                    # Update playtime before exiting
                    update_playtime(me, session_start, save_mgr)
                    return  # Exit the main function
                elif check == "logout":
                    # Break inner loop to go back to login
                    running = False
                    # Update playtime before logging out
                    update_playtime(me, session_start, save_mgr)
                    print("\nReturning to login screen...\n")
                    time.sleep(1)
                    os.system("clear")
        
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            print("\n\nEmergency shutdown initiated. Saving game...")
            save_mgr = SaveManager()
            # Update playtime before emergency exit
            update_playtime(me, session_start, save_mgr)
            if save_mgr.save_game(me):
                print("Game saved successfully. Goodbye!")
            else:
                print("Warning: Game could not be saved.")
            break
        except Exception as e:
            # Handle unexpected errors
            print(f"\nUnexpected error: {e}")
            print("Game will restart...")
            time.sleep(2)

# Helper function to update player's playtime
def update_playtime(player_obj, session_start, save_mgr):
    """Update player's total playtime by adding the current session time"""
    try:
        session_end = datetime.datetime.now()
        session_duration = (session_end - session_start).total_seconds()
        
        # Update playtime directly on the player object
        if hasattr(player_obj, "playtime"):
            player_obj.playtime += session_duration
        else:
            player_obj.playtime = session_duration
            
        # Save the updated playtime with the player data
        save_mgr.save_game(player_obj)
    except Exception as e:
        print(f"Error updating playtime: {e}")

# yeah if ykyk
if __name__ == "__main__":
    main()