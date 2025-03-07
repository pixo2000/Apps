import player
from dimension import Dimension
from player_functions import scan_system, display_scan_results

def handle_input(name):
    command = input(f"\n[{name.position('dimension')}:{name.position('x')},{name.position('y')}] {name.name} > ").lower()
    
    if command.startswith("move "): # move 7 3
        parts = command.split(" ")
        if len(parts) != 3:
            print("\n✗ Invalid move command. Format: move X Y\n")
            return "positive"
        try:
            x = int(parts[1])
            y = int(parts[2])
            name.move(x,y)
            return "positive"
        except ValueError:
            print("\n✗ Invalid coordinates. Please enter numbers.\n")
            return "positive"
            
    elif command == "whereami":
        dimension = name.position('dimension')
        x_pos = name.position('x')
        y_pos = name.position('y')
        
        print("\n=== CURRENT LOCATION ===")
        print(f"» Dimension: {dimension}")
        print(f"» Coordinates: [{x_pos}, {y_pos}]")
        try:
            dim_title = name.dimension.title
            print(f"» System: {dim_title}")
        except AttributeError:
            pass
        print("=======================\n")
        return "positive"
        
    elif command.startswith("jump "): # jump A01
        dimension_name = command.split(" ")[1].upper()
        name.jump(dimension_name)
        return "positive"
        
    elif command == "dimensions":
        available = Dimension.get_available_dimensions()
        
        print("\n=== AVAILABLE DIMENSIONS ===")
        for i, dim in enumerate(available):
            try:
                temp_dim = Dimension(dim)
                print(f"» {dim}: {temp_dim.title} - {temp_dim.description}")
            except:
                print(f"» {dim}")
        print("===========================\n")
        return "positive"
        
    elif command == "scan":
        scan_results = scan_system(name)
        display_scan_results(scan_results)
        return "positive"
        
    elif command in ["quit", "exit"]:
        print("\n=== SYSTEM SHUTDOWN ===")
        print("Saving data...")
        print("Closing connections...")
        print("\nGoodbye Captain! Safe travels.\n")
        return "negative"
        
    elif command == "help":
        display_help()
        return "positive"
        
    else:
        print("\n✗ Unknown command. Type 'help' for available commands.\n")
        return "positive"

def display_help():
    print("\n" + "=" * 50)
    print("             COMMAND REFERENCE")
    print("=" * 50)
    
    commands = [
        ("move X Y", "Navigate to coordinates X, Y"),
        ("whereami", "Display current location information"),
        ("jump DIM", "Jump to dimension DIM (e.g. A01, C12)"),
        ("dimensions", "List all available dimensions"),
        ("scan", "Scan current system for celestial bodies"),
        ("quit/exit", "Exit the game"),
        ("help", "Display this help message")
    ]
    
    for cmd, desc in commands:
        print(f"» {cmd.ljust(15)} - {desc}")
    
    print("=" * 50 + "\n")