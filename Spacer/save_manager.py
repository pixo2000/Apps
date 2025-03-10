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
    
    def is_valid_player_name(self, name):
        """
        Check if player name meets requirements:
        - 3-15 characters long
        - Can contain uppercase letters (A-Z)
        - Can contain lowercase letters (a-z)
        - Can contain numbers (0-9)
        - Can contain underscores (_)
        """
        return bool(self.name_pattern.match(name))
        
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
        
        # We store files with lowercase names but preserve the display name in the file
        save_path = self.save_directory / f"{player.name.lower()}.json"
        
        try:
            with open(save_path, 'w') as save_file:
                json.dump(save_data, save_file, indent=4)
            return True
        except Exception as e:
            print(f"\n⚠ Save error: {str(e)}")
            return False
    
    def load_game(self, player_name):
        """Load a player's game state from their save file"""
        save_path = self.save_directory / f"{player_name.lower()}.json"
        
        if not save_path.exists():
            return None
        
        try:
            with open(save_path, 'r') as save_file:
                data = json.load(save_file)
                
                # Don't allow loading dead players
                if data.get("is_dead", False):
                    print(f"\n☠ Captain {data['name']} is deceased. Their journey has ended.")
                    return None
                    
                return data
        except Exception as e:
            print(f"\n⚠ Load error: {str(e)}")
            return None
    
    def player_exists(self, player_name):
        """Check if a save file exists for a player"""
        save_path = self.save_directory / f"{player_name.lower()}.json"
        return save_path.exists()
    
    def is_player_dead(self, player_name):
        """Check if a player is dead"""
        save_path = self.save_directory / f"{player_name.lower()}.json"
        if not save_path.exists():
            return False
            
        try:
            with open(save_path, 'r') as save_file:
                data = json.load(save_file)
                return data.get("is_dead", False)
        except:
            return False
    
    def get_all_players(self):
        """Return a list of all saved players that aren't dead"""
        players = []
        for save_file in self.save_directory.glob('*.json'):
            try:
                with open(save_file, 'r') as f:
                    data = json.load(f)
                    if not data.get("is_dead", False):
                        # Use the name stored in the file, not the filename
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
            
        # Get old name and save file path
        old_name = player.name
        old_save_path = self.save_directory / f"{old_name.lower()}.json"
        
        # Change the name in the player object
        player.change_name(new_name)
        
        # Save with the new name
        if not self.save_game(player):
            # If save fails, revert name change
            player.change_name(old_name)
            return False, "Failed to save with new name"
        
        # Delete the old save file
        try:
            if old_save_path.exists():
                old_save_path.unlink()
        except Exception as e:
            # If we can't delete the old file, that's not critical
            # The new save already exists
            pass
            
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
