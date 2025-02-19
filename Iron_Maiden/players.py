import playground

class Player:
    def __init__(self, name, team, position, health=100, attack=10):
        self.name = name
        self.team = team
        self.position = position
        self.health = health
        self.attack = attack

    def place_on_playground(self, playground_instance):
        playground_instance = playground.write(playground_instance, self.position[0], self.position[1], self.name)
        return playground_instance

def init(playground_instance):
    team_1 = [Player("E", 1, (1, 1)),
              Player("C", 1, (1, 2)),
              Player("A", 1, (1, 3)),
              Player("B", 1, (1, 4)),
              Player("D", 1, (1, 5))]
    team_2 = [Player("W", 2, (5, 1)),
              Player("X", 2, (5, 2)),
              Player("Z", 2, (5, 3)),
              Player("Y", 2, (5, 4)),
              Player("V", 2, (5, 5))]

    for player in team_1 + team_2:
        playground_instance = player.place_on_playground(playground_instance)

    return playground_instance