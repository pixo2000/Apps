import player
from dimension import Dimension

def handle_input(name):
    command = input(f"{name.name}, what do you want to do? ")
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
        name.position()
        return "positive"
    elif command.startswith("jump "): # jump A01
        dimension_name = command.split(" ")[1]
        name.jump(dimension_name)
        return "positive"
    elif command == "dimensions":
        print("Available dimensions:")
        for dim in Dimension.get_available_dimensions():
            print(f"- {dim}")
        return "positive"
    elif command in ["quit", "exit"]:
        print("Goodbye Captain!")
        return "negative"
    else:
        print("Invalid command.")
        return "positive"