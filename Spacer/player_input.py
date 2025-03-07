import player
from dimension import Dimension
from player_functions import scan_system, display_scan_results

def handle_input(name):
    command = input(f"{name.name}, what do you want to do? ").lower()
    if command.startswith("move "): # move 7 3
        parts = command.split(" ")
        if len(parts) != 3:
            print("Invalid move command.")
            return "positive"
        try:
            x = int(parts[1])
            y = int(parts[2])
            name.move(x,y)
            return "positive"
        except ValueError:
            print("Invalid move command.")
            return "positive"
    elif command == "whereami":
        print(f"You are at position {name.position('x')}, {name.position('y')} in dimension {name.position('dimension')}")
        return "positive"
    elif command.startswith("jump "): # jump A01
        dimension_name = command.split(" ")[1].upper()  # Konvertieren zu Großbuchstaben
        name.jump(dimension_name)
        return "positive"
    elif command == "dimensions":
        print("Available dimensions:")
        for dim in Dimension.get_available_dimensions():
            print(f"- {dim}")
        return "positive"
    elif command == "scan":
        scan_results = scan_system(name)
        display_scan_results(scan_results)
        return "positive"
    elif command in ["quit", "exit"]:
        print("Goodbye Captain!")
        return "negative"
    elif command == "help":
        display_help()
        return "positive"
    else:
        print("Invalid command.")
        return "positive"

def display_help():
    print("\n=== COMMAND HELP ===")
    print("move X Y - Move to coordinates X, Y")
    print("whereami - Display current location")
    print("jump DIM - Jump to dimension DIM (e.g. A01, C12)")
    print("dimensions - List all available dimensions")
    print("scan - Scan current system for celestial bodies")
    print("quit/exit - Exit the game")
    print("help - Display this help message")
    print("===================\n")