from OpenGL.GL import *
from OpenGL.GLU import *
import pygame

def setup_display(width=800, height=600):
    pygame.display.set_mode((width, height), pygame.DOUBLEBUF | pygame.OPENGL)

def render(game_state):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # Apply camera transformations
    glTranslatef(0, 0, game_state.zoom)
    glRotatef(game_state.camera_rot, 0, 1, 0)
    glTranslatef(-game_state.camera_pos[0], -game_state.camera_pos[1], -game_state.camera_pos[2])

    # Draw coordinate grid
    draw_grid(game_state)

    # Draw stations
    for station in game_state.stations:
        draw_station(station, station == game_state.selected_station)

    pygame.display.flip()

def draw_grid(game_state):
    # Draw main grid
    glBegin(GL_LINES)
    glColor3f(0.3, 0.3, 0.4)  # Brighter grid color
    for i in range(-40, 41, 4):  # Larger grid
        glVertex3f(i, 0, -40)
        glVertex3f(i, 0, 40)
        glVertex3f(-40, 0, i)
        glVertex3f(40, 0, i)
    glEnd()
    
    # Draw connecting lines between stations
    glBegin(GL_LINES)
    glColor3f(0.5, 0.5, 0.0)  # Golden lines
    for i, station1 in enumerate(game_state.stations):
        for station2 in game_state.stations[i+1:]:
            glVertex3f(*station1['pos'])
            glVertex3f(*station2['pos'])
    glEnd()

def draw_station(station, selected):
    glPushMatrix()
    glTranslatef(*station['pos'])
    
    if selected:
        glColor3f(1.0, 1.0, 0.0)  # Yellow for selected station
        scale = 2.0  # Larger when selected
    else:
        glColor3f(*station['color'])
        scale = 1.5  # Larger default size
    
    glScalef(scale, scale, scale)
    
    # Draw station as a cube
    glBegin(GL_QUADS)
    # Front face
    glVertex3f(-0.5, -0.5, 0.5)
    glVertex3f(0.5, -0.5, 0.5)
    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    # Back face
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(-0.5, 0.5, -0.5)
    glVertex3f(0.5, 0.5, -0.5)
    glVertex3f(0.5, -0.5, -0.5)
    # Top face
    glVertex3f(-0.5, 0.5, -0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(0.5, 0.5, -0.5)
    # Bottom face
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(0.5, -0.5, -0.5)
    glVertex3f(0.5, -0.5, 0.5)
    glVertex3f(-0.5, -0.5, 0.5)
    # Right face
    glVertex3f(0.5, -0.5, -0.5)
    glVertex3f(0.5, 0.5, -0.5)
    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(0.5, -0.5, 0.5)
    # Left face
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(-0.5, -0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5, -0.5)
    glEnd()
    
    glPopMatrix()