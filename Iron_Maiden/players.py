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