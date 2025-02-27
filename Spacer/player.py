import time

class Player:
    def __init__(self, name):
        self.name = name
        self.x = 0
        self.y = 0
        self.dimension = A01
    
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

    def position(self):
        print(f"Current coordinates: {self.x}, {self.y}")

    def jump(self, dimension):
        print(f"Jumping to {dimension.name}")
