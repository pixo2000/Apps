import pygame
import playground

# Initialize Pygame
pygame.init()

# Constants
CELL_SIZE = 50
GRID_SIZE = 7
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Set up the display
screen = pygame.display.set_mode((GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE))
pygame.display.set_caption(" Iron Maiden")

def draw_playground(playground_instance):
    screen.fill(WHITE)
    for y, line in enumerate(playground_instance):
        for x, cell in enumerate(line):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if cell == "1":
                pygame.draw.circle(screen, GREEN, rect.center, CELL_SIZE // 2 - 5)
            pygame.draw.rect(screen, BLACK, rect, 1)
    pygame.display.flip()

def main():
    playground_instance = playground.generate()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        draw_playground(playground_instance)
        pygame.time.wait(100)

    pygame.quit()