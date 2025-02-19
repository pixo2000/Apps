import pygame
import math

def handle_input(keys, game_state):
    if not game_state.moving_to_station:
        if keys[pygame.K_a]:
            game_state.camera_rot += 2
        if keys[pygame.K_d]:
            game_state.camera_rot -= 2
        if keys[pygame.K_w]:
            game_state.camera_pos[0] += math.sin(math.radians(game_state.camera_rot))
            game_state.camera_pos[2] += math.cos(math.radians(game_state.camera_rot))
            game_state.move_timer = 1.0
        if keys[pygame.K_s]:
            game_state.camera_pos[0] -= math.sin(math.radians(game_state.camera_rot))
            game_state.camera_pos[2] -= math.cos(math.radians(game_state.camera_rot))
            game_state.move_timer = 1.0
        if keys[pygame.K_r]:
            game_state.camera_pos[1] += 1
            game_state.move_timer = 1.0
        if keys[pygame.K_f]:
            game_state.camera_pos[1] -= 1
            game_state.move_timer = 1.0
        if keys[pygame.K_x]:
            game_state.zoom -= 0.5
        if keys[pygame.K_y]:
            game_state.zoom += 0.5
        if keys[pygame.K_g]:
            game_state.reset_camera()

def find_nearest_station(game_state):
    nearest = None
    min_dist = float('inf')
    for station in game_state.stations:
        dx = station['pos'][0] - game_state.camera_pos[0]
        dy = station['pos'][1] - game_state.camera_pos[1]
        dz = station['pos'][2] - game_state.camera_pos[2]
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        if dist < min_dist:
            min_dist = dist
            nearest = station
    return nearest