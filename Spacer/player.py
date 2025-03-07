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
        
        # Show countdown and wait for each field
        for remaining in range(distance, 0, -1):
            print(f"Moving... {remaining} seconds remaining")
            time.sleep(1)
            
        # Update position
        self.x = x
        self.y = y

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
            print(f"Jumping to {new_dimension.title}...")
            
            # Ladeleiste anzeigen
            for _ in tqdm(range(20), desc="Jumping", ncols=100): # change loading bar style
                time.sleep(0.1)

            self.dimension = new_dimension
            self.x = 10
            self.y = 10
            print(f"Welcome to {new_dimension.title}: {new_dimension.description}")
        except ValueError as e:
            print(str(e))
