"""
Game state management for Spacer.
"""

class GameState:
    def __init__(self, player):
        self.player = player

    def restart_game(self):
        """Restart the game"""
        print("\nRestarting game...")
        self.player.is_dead = False
        self.player.x = 0
        self.player.y = 0
        self.player.dimension = None
        self.player.known_dimensions = []
        self.player.known_bodies = {}
        self.player.docked_at = None

    def process_command(self, command):
        """Process a command from the player"""
        # If player is dead, only allow 'restart' command
        if self.player.is_dead:
            if command.lower() == "restart":
                self.restart_game()
                return
            else:
                print("\n✗ You have died. Type 'restart' to begin a new game.\n")
                return

        # Check if player is at a station and process station-specific commands
        if self.player.docked_at:
            station = self.player.docked_at
            if station.handle_command(command, self.player):
                return

        # Handle normal space commands
        print("\nCommand not recognized. Type 'help' for a list of commands.\n")