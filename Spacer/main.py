# import other files
import player
import player_input as pinput
from save_manager import SaveManager

# import modules
import time
import os

# load stuff
def temp_start():
    os.system("clear")
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
    
    if saved_players:
        print("Saved captains found:")
        for i, saved_name in enumerate(saved_players, 1):
            print(f"{i}. {saved_name}")
        
        while True:
            choice = input("\nEnter captain name to continue, or 'new' for new game: ")
            
            if choice.lower() == 'new':
                return create_new_captain(save_mgr)
            
            # Case-insensitive player name check
            for saved_name in saved_players:
                if saved_name.lower() == choice.lower():
                    return saved_name, True, False  # Return exact name, load_save flag, show_tutorial flag
            
            print("Captain not found. Please try again.")
    else:
        return create_new_captain(save_mgr)

def create_new_captain(save_mgr):
    """Handle creation of a new captain with name validation"""
    while True:
        name = input("Who are you, Captain? ")
        
        # Check length and allowed characters
        if not save_mgr.is_valid_player_name(name):
            print("\n⚠ Invalid name. Names must be 3-15 characters long and contain")
            print("  only letters, numbers, and underscores.")
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
        
        return name, False, True  # New captain, don't load save, show tutorial

# main loop
def main():
    # Loop to handle logout and new login
    current_player = None  # Track the current player to save on exit
    save_mgr = SaveManager()  # Create save manager instance once
    
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
            current_player = me  # Set reference to current player for emergency save
            
            # Load saved game if requested
            if load_save:
                save_data = save_mgr.load_game(name)
                if me.load_save_data(save_data):
                    print(f"\nWelcome back, Captain {name}!")
                    print(f"Resuming from {me.dimension.title}, coordinates [{me.x}, {me.y}]")
                else:
                    print("\nError loading save. Starting new game.")
                    show_help = True  # Show help if load failed
            
            # Show help menu for new players
            if show_help:
                pinput.display_help(first_time=True)
            
            running = True
            
            while running:
                check = pinput.handle_input(me)
                if check == "negative":
                    # Exit the game entirely
                    running = False
                    return  # Exit the main function
                elif check == "logout":
                    # Break inner loop to go back to login
                    running = False
                    print("\nReturning to login screen...\n")
                    time.sleep(1)
                    os.system("clear")
        
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully with save
            print("\n\nEmergency shutdown initiated!")
            
            # Save the current player's progress if one exists
            if current_player and not current_player.is_dead:
                print("Saving your progress before exit...")
                save_mgr.save_game(current_player)
                print(f"Progress saved for Captain {current_player.name}.")
                
            print("Goodbye, Captain! Safe travels.")
            break
        except Exception as e:
            # Handle unexpected errors
            print(f"\nUnexpected error: {e}")
            
            # Try to save current player if one exists
            if current_player and not current_player.is_dead:
                print("Attempting to save your progress...")
                try:
                    save_mgr.save_game(current_player)
                    print(f"Progress saved for Captain {current_player.name}.")
                except:
                    print("Failed to save progress during error recovery.")
                    
            print("Game will restart...")
            time.sleep(2)


# yeah if ykyk
if __name__ == "__main__":
    main()