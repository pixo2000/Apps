import pygame
from pygame import font

import playground

# Initialize Pygame
pygame.init()

# Constants
screen = None
CELL_SIZE = 50
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# Set up the display
def init(playground_instance):
    global screen
    GRID_SIZE = len(playground_instance)
    screen = pygame.display.set_mode((GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE))
    pygame.display.set_caption("Iron Maiden")

def draw_playground(playground_instance):
    global screen
    screen.fill(WHITE)
    font = pygame.font.Font(None, 36)  # Use a default font and size 36
    for y, line in enumerate(playground_instance):
        for x, cell in enumerate(line):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if cell == "A":
                pygame.draw.circle(screen, BLUE, rect.center, CELL_SIZE // 2 - 5)
                text = font.render("A", True, BLACK)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)
            elif cell == "B":
                pygame.draw.circle(screen, GREEN, rect.center, CELL_SIZE // 2 - 5)
                text = font.render("B", True, BLACK)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)
            elif cell == "C":
                pygame.draw.circle(screen, GREEN, rect.center, CELL_SIZE // 2 - 5)
                text = font.render("C", True, BLACK)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)
            elif cell == "D":
                pygame.draw.circle(screen, GREEN, rect.center, CELL_SIZE // 2 - 5)
                text = font.render("D", True, BLACK)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)
            elif cell == "E":
                pygame.draw.circle(screen, GREEN, rect.center, CELL_SIZE // 2 - 5)
                text = font.render("E", True, BLACK)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)
            elif cell == "V":
                pygame.draw.circle(screen, RED, rect.center, CELL_SIZE // 2 - 5)
                text = font.render("V", True, BLACK)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)
            elif cell == "W":
                pygame.draw.circle(screen, RED, rect.center, CELL_SIZE // 2 - 5)
                text = font.render("W", True, BLACK)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)
            elif cell == "X":
                pygame.draw.circle(screen, RED, rect.center, CELL_SIZE // 2 - 5)
                text = font.render("X", True, BLACK)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)
            elif cell == "Y":
                pygame.draw.circle(screen, RED, rect.center, CELL_SIZE // 2 - 5)
                text = font.render("Y", True, BLACK)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)
            elif cell == "Z":
                pygame.draw.circle(screen, RED, rect.center, CELL_SIZE // 2 - 5)
                text = font.render("Z", True, BLACK)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)
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