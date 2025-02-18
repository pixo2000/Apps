import playground

class Player:
    def __init__(self, name, team, position):
        self.name = name
        self.team = team
        self.position = position

    def place_on_playground(self, playground_instance):
        playground_instance = playground.write(playground_instance, self.position[0], self.position[1], self.name)
        return playground_instance

class NPC(Player):
    def __init__(self, name, team, position, difficulty):
        super().__init__(name, team, position)
        self.difficulty = difficulty

def init(playground_instance):
    team_1 = [Player("E", 1, (1, 1)), Player("C", 1, (1, 2)), Player("A", 1, (1, 3)), Player("B", 1, (1, 4)), Player("D", 1, (1, 5))]
    team_2 = [NPC("W", 2, (5, 1), "hard"), NPC("X", 2, (5, 2), "medium"), NPC("Z", 2, (5, 3), "easy"), NPC("Y", 2, (5, 4), "medium"), NPC("V", 2, (5, 5), "hard")]

    for player in team_1 + team_2:
        playground_instance = player.place_on_playground(playground_instance)

    return playground_instance