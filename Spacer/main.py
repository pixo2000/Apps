# import other files
import player
import player_input as pinput

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
    
    name = input("Who are you, Captain? ")
    print("\n" + "*" * 50)
    print(f"Welcome aboard, Captain {name}!")
    print("Your journey through the cosmos begins now.")
    print("*" * 50 + "\n")
    time.sleep(1)
    
    return name

# global values


# main loop
def main():
    name = temp_start() # replace later
    me = player.Player(name)
    running = True
    
    while running:
        check = pinput.handle_input(me)
        if check == "negative":
            running = False


# yeah if ykyk
if __name__ == "__main__":
    main()