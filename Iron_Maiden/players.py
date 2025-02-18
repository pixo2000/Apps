import playground

def init(playground_instance):
    # Team 1
    playground_instance = playground.write(playground_instance, 1, 1, "E") # Player 5
    playground_instance = playground.write(playground_instance, 1, 2, "C") # Player 3
    playground_instance = playground.write(playground_instance, 1, 3, "A") # Player 1
    playground_instance = playground.write(playground_instance, 1, 4, "B") # Player 2
    playground_instance = playground.write(playground_instance, 1, 5, "D") # Player 4
    # Team 2
    playground_instance = playground.write(playground_instance, 5, 1, "W") # Player 5
    playground_instance = playground.write(playground_instance, 5, 2, "X") # Player 3
    playground_instance = playground.write(playground_instance, 5, 3, "Z") # Player 1
    playground_instance = playground.write(playground_instance, 5, 4, "Y") # Player 2
    playground_instance = playground.write(playground_instance, 5, 5, "V") # Player 4

    return  playground_instance


# Testing with classes for NBT attributes
class Player:
    def __init__(self, name, team, position):
        self.name = name
        self.team = team
        self.position = position

    def place_on_playground(self, playground_instance):
        playground_instance = playground.write(playground_instance, self.team, self.position, self.name)
        return playground_instance

class NPC(Player):
    def __init__(self, name, team, position, difficulty):
        super().__init__(name, team, position)
        self.difficulty = difficulty