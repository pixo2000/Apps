import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *
import math
import random
from state import GameState
from movement import handle_input, find_nearest_station
from rendering import setup_display, render

# Initialize Pygame and OpenGL
pygame.init()
display = (800, 600)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

# Set up display
setup_display(800, 600)

def main():
    game_state = GameState()
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                # Select nearest station when zoomed in
                if game_state.zoom > -15:
                    game_state.selected_station = find_nearest_station(game_state)

        keys = pygame.key.get_pressed()
        handle_input(keys, game_state)
        game_state.update()
        render(game_state)
        
        clock.tick(60)

if __name__ == '__main__':
    main()