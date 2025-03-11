import json
import os
import re
from pathlib import Path

class SaveManager:
    def __init__(self):
        self.save_directory = Path(os.path.dirname(__file__)) / 'saves'
        # Ensure the saves directory exists
        self.save_directory.mkdir(exist_ok=True)
        
        # Valid player name pattern: 3-15 chars, alphanumeric (both upper and lowercase) and underscore
        self.name_pattern = re.compile(r'^[a-zA-Z0-9_]{3,15}$')
        
        # List of reserved names that cannot be used for players
        self.reserved_names = ["new", "exit", "quit", "logout", "help"]
    
    def is_valid_player_name(self, name):
        """
        Check if player name meets requirements:
        - 3-15 characters long
        - Can contain uppercase letters (A-Z)
        - Can contain lowercase letters (a-z)
        - Can contain numbers (0-9)
        - Can contain underscores (_)
        - Cannot be a reserved command name
        """
        # First check if name matches pattern requirements
        if not bool(self.name_pattern.match(name)):
            return False
        
        # Then check if it's not a reserved name (case-insensitive)
        if name.lower() in self.reserved_names:
            return False
        
        return True
        
    def save_game(self, player):
        """Save the player's game state to a JSON file"""
        save_data = {
            "name": player.name,
            "uuid": player.uuid,  # Store the player's UUID
            "position": {
                "x": player.x,
                "y": player.y,
                "dimension": player.dimension.name
            },
            "discoveries": {
                "known_dimensions": player.known_dimensions,
                "known_bodies": player.known_bodies
            },
            "is_dead": player.is_dead
        }
        
        # Use the UUID for the filename instead of the player name
        save_path = self.save_directory / f"{player.uuid}.json"
        
        try:
            with open(save_path, 'w') as save_file:
                json.dump(save_data, save_file, indent=4)
            return True
        except Exception as e:
            print(f"\n⚠ Save error: {str(e)}")
            return False
    
    def load_game(self, player_name):
        """Load a player's game state from their save file"""
        # We need to search for the player by name in all save files
        for save_file in self.save_directory.glob('*.json'):
            try:
                with open(save_file, 'r') as f:
                    data = json.load(f)
                    # Case-insensitive name comparison
                    if data.get("name", "").lower() == player_name.lower():
                        # Don't allow loading dead players
                        if data.get("is_dead", False):
                            print(f"\n☠ Captain {data['name']} is deceased. Their journey has ended.")
                            return None
                        return data
            except:
                # Skip files that can't be read properly
                continue
        
        return None
    
    def player_exists(self, player_name):
        """Check if a save file exists for a player"""
        # We need to search through all save files to find the player by name
        for save_file in self.save_directory.glob('*.json'):
            try:
                with open(save_file, 'r') as f:
                    data = json.load(f)
                    if data.get("name", "").lower() == player_name.lower():
                        return True
            except:
                # Skip files that can't be read properly
                continue
        
        return False
    
    def is_player_dead(self, player_name):
        """Check if a player is dead"""
        # We need to search through all save files to find the player by name
        for save_file in self.save_directory.glob('*.json'):
            try:
                with open(save_file, 'r') as f:
                    data = json.load(f)
                    if data.get("name", "").lower() == player_name.lower():
                        return data.get("is_dead", False)
            except:
                # Skip files that can't be read properly
                continue
        
        return False
    
    def get_all_players(self):
        """Return a list of all saved players that aren't dead"""
        players = []
        for save_file in self.save_directory.glob('*.json'):
            try:
                with open(save_file, 'r') as f:
                    data = json.load(f)
                    if not data.get("is_dead", False):
                        # Use the name stored in the file
                        players.append(data["name"])
            except:
                # Skip files that can't be read properly
                continue
        return players

    def change_player_name(self, player, new_name):
        """Change a player's name and update the save file"""
        if not self.is_valid_player_name(new_name):
            return False, "Invalid name format"
            
        # Check if the new name already exists
        if self.player_exists(new_name):
            return False, "Name already taken"
            
        # Store old name
        old_name = player.name
        
        # Change the name in the player object
        player.change_name(new_name)
        
        # Save with the new name - no need to delete old file as filename is UUID-based
        if not self.save_game(player):
            # If save fails, revert name change
            player.change_name(old_name)
            return False, "Failed to save with new name"
            
        return True, f"Name changed successfully to {new_name}"
        
    def find_player_by_uuid(self, uuid_to_find):
        """Find a player by their UUID"""
        for save_file in self.save_directory.glob('*.json'):
            try:
                with open(save_file, 'r') as f:
                    data = json.load(f)
                    if data.get("uuid") == uuid_to_find:
                        return data
            except:
                continue
        return None
