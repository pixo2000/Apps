# Import other Files
import playground
import visual
import players

# Import Modules
import time
import pygame

# Global Variables
playground_instance = None
running = True

# Main loop halt
def main():
    global playground_instance, running

    # Initialize the playground
    playground_instance = playground.generate()
    visual.init(playground_instance)

    # Main Code for changes
    playground.show(playground_instance)
    playground_instance = players.init(playground_instance)
    playground.show(playground_instance)

    # Main loop to handle events and visual updates
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                return
        visual.draw_playground(playground_instance)
        time.sleep(0.1)


# yeah whatever you think its true
if __name__ == '__main__':
    main()