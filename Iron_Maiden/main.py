# Import other Files
import playground
import visual

# Import Modules
import threading
import time
import pygame

# Global Variables
playground_instance = None
running = True

# Update loop -> maybe zu visual verschieben
def update_visual():
    global playground_instance, running
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                return
        visual.draw_playground(playground_instance)
        time.sleep(1)


# Main loop halt
def main():
    global playground_instance

    playground_instance = playground.generate()

    # Start Visual Thread
    visual_thread = threading.Thread(target=update_visual)
    visual_thread.daemon = True
    visual_thread.start()

    # Modify the playground
    playground.show(playground_instance)
    playground_instance = playground.write(playground_instance, 1, 1, "1")
    value = playground.read(playground_instance, 1, 1)
    playground.show(playground_instance)
    visual.draw_playground(playground_instance)
    print(f"Value at (1, 1): {value}")

    # Keep the main thread running to allow visual updates
    while True:
        time.sleep(1)

if __name__ == '__main__':
    main()