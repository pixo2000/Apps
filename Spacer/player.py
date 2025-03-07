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
        for remaining in range(distance, 0, -1):
            progress = distance - remaining
            bar_length = 20
            progress_bar = "█" * int((progress/distance) * bar_length) + "▒" * (bar_length - int((progress/distance) * bar_length))
            percent = int((progress/distance) * 100)
            
            # Display movement animation
            if remaining > 1:
                print(f"\r[{bar_length}] Moving... {remaining} fields remaining [{percent}%] {bar_length}", end="", flush=True)
                time.sleep(1)
            else:
                print(f"\r[{bar_length}] Moving... Final approach [{percent}%] {bar_length}", end="", flush=True)
                time.sleep(1)
                
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
