import time
from dimension import Dimension
from tqdm import tqdm

class Player:
    def __init__(self, name):
        self.name = name
        self.x = 10
        self.y = 10
        self.dimension = Dimension('A01')
    
    def move(self, x, y):
        # Calculate the distance (maximum of x or y difference for diagonal movement)
        distance = max(abs(x - self.x), abs(y - self.y))
        
        if distance == 0:
            print("\n✓ Already at the requested coordinates.\n")
            return
            
        print(f"\n➤ Setting course to coordinates [{x}, {y}]")
        
        # Show countdown and wait for each field
        for i in range(distance + 1):  # +1 to ensure we reach 100%
            progress = i
            bar_length = 30
            
            # Create a dynamic spaceship movement animation
            ship_position = int((progress/distance) * (bar_length-3)) if distance > 0 else bar_length-3
            spacebar = "·" * ship_position + "🚀" + "·" * (bar_length - ship_position - 3)
            percent = int((progress/distance) * 100) if distance > 0 else 100
            
            # Display improved movement animation with spaceship
            if i < distance:
                remaining = distance - i
                line_content = f"[{spacebar}] Moving... {remaining} second{'s' if remaining > 1 else ' '} remaining [{percent}%]"
            else:
                # Final frame shows 100%
                line_content = f"[{spacebar}] Moving... Arrival imminent [100%]"
                
            # Ensure the line is properly cleared with padding
            print(f"\r{line_content}{' ' * 10}", end="", flush=True)
            
            if i < distance:  # Don't sleep after the last frame
                time.sleep(0.8)
                
        # Update position
        self.x = x
        self.y = y
        print(f"\n\n✓ Arrived at coordinates [{x}, {y}]\n")

    def position(self, variable):
        if variable == "x":
            return self.x
        elif variable == "y":
            return self.y
        elif variable == "dimension":
            return self.dimension.name

    def jump(self, dimension_name):
        try:
            new_dimension = Dimension(dimension_name)
            print(f"\n▼ DIMENSIONAL JUMP SEQUENCE INITIATED ▼")
            print(f"➤ Target: {new_dimension.title}")
            print(f"➤ Preparing and calibrating jump engines...")
            
            # Ladeleiste anzeigen
            for _ in tqdm(range(100), desc="Charging", ncols=100, ascii='░▒█', bar_format='{l_bar}[{bar}]'): # change loading bar style
                time.sleep(0.1)

            print(f"\n➤ Jump sequence activated! Entering hyperspace...")
            time.sleep(1)
            
            # Animation für den Sprung
            jump_animation = ["■□□□□", "□■□□□", "□□■□□", "□□□■□", "□□□□■", "□□□■□", "□□■□□", "□■□□□"]
            for _ in range(3):  # 3 cycles of animation
                for frame in jump_animation:
                    print(f"\r▻▻▻ {frame} ◅◅◅", end="", flush=True)
                    time.sleep(0.1)
            
            self.dimension = new_dimension
            self.x = 10
            self.y = 10
            
            print(f"\n\n✓ JUMP COMPLETE")
            print(f"\n== Welcome to {new_dimension.title} ==")
            print(f"» {new_dimension.description}")
            print(f"» Starting coordinates: [10, 10]\n")
            
        except ValueError as e:
            print(f"\n✗ JUMP FAILED: {str(e)}\n")
