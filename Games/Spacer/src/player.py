"""
Player module for the Spacer game.
"""

class Player:
    def __init__(self, name="Player", x=0, y=0):
        self.name = name
        self.x = x
        self.y = y
        self.dimension = None
        self.known_dimensions = []
        self.known_bodies = {}
        self.docked_at = None  # Track when docked at stations
        self.is_dead = False