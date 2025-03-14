import json
import os
import re
from pathlib import Path
import datetime

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

    def format_date(self, date_str=None):
        """Format a date to DD.MM.YY - HH:MM format using Berlin timezone"""
        try:
            # If no date provided, use current time
            if date_str is None:
                dt = datetime.datetime.now()
            # If a string is provided, try to parse it
            elif isinstance(date_str, str):
                dt = datetime.datetime.fromisoformat(date_str)
            # If already a datetime object, use it directly
            elif isinstance(date_str, datetime.datetime):
                dt = date_str
            else:
                return str(date_str)  # Fallback
            
            # Convert to Berlin time if possible
            try:
                import pytz
                berlin_tz = pytz.timezone('Europe/Berlin')
                if dt.tzinfo is None:
                    # Assume UTC for naive datetime objects
                    dt = dt.replace(tzinfo=datetime.timezone.utc)
                dt = dt.astimezone(berlin_tz)
            except ImportError:
                # If pytz is not available, use system local time
                pass
                
            # Format with colon separator in time portion
            return dt.strftime("%d.%m.%y - %H:%M")
        except:
            # If parsing fails, return original or current date
            return date_str if date_str else datetime.datetime.now().isoformat()
        
    def format_playtime(self, seconds):
        """Format playtime from seconds to 'days:hours:minutes:seconds' format"""
        # Calculate components
        days = int(seconds // (24 * 3600))
        seconds %= (24 * 3600)
        hours = int(seconds // 3600)
        seconds %= 3600
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        
        # Format as days:hours:minutes:seconds with leading zeros
        return f"{days:02d}:{hours:02d}:{minutes:02d}:{seconds:02d}"

    def parse_playtime(self, playtime_str):
        """Parse a playtime string back into seconds"""
        try:
            # Handle legacy format (raw seconds)
            if isinstance(playtime_str, (int, float)):
                return playtime_str
            
            # Handle colon-separated format (dd:hh:mm:ss)
            if ":" in playtime_str and playtime_str.count(":") == 3:
                days, hours, minutes, seconds = map(int, playtime_str.split(":"))
                return days * 86400 + hours * 3600 + minutes * 60 + seconds
            
            # Handle old verbose format (Days:X, Hours:Y, Minutes:Z, Seconds:W)
            if "Days:" in playtime_str:
                parts = playtime_str.split(", ")
                days = int(parts[0].replace("Days:", ""))
                hours = int(parts[1].replace("Hours:", ""))
                minutes = int(parts[2].replace("Minutes:", ""))
                seconds = int(parts[3].replace("Seconds:", ""))
                return days * 86400 + hours * 3600 + minutes * 60 + seconds
            
            # Handle numeric string
            return float(playtime_str)
        except Exception:
            return 0  # Default to 0 if parsing fails

    def save_game(self, player):
        """Save the player's game state to a JSON file"""
        # Get current time for last_login update
        current_time = self.format_date(datetime.datetime.now())
        
        # Format creation date if it exists, otherwise use current time
        creation_date = getattr(player, "creation_date", None)
        formatted_creation = self.format_date(creation_date) if creation_date else current_time
        
        # Format playtime for storage
        raw_playtime = getattr(player, "playtime", 0)
        formatted_playtime = self.format_playtime(raw_playtime)
        
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
            "playtime": formatted_playtime,  # Store formatted playtime string
            "creation_date": formatted_creation,  # Format the creation date
            "last_login": current_time,  # Store formatted last login date
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
        
    def get_all_players_including_dead(self):
        """Return a list of all saved players including dead ones"""
        players = []
        for save_file in self.save_directory.glob('*.json'):
            try:
                with open(save_file, 'r') as f:
                    data = json.load(f)
                    # Include all players regardless of dead status
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
