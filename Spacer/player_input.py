import datetime
import player
from dimension import Dimension
from player_functions import scan_system
from save_manager import SaveManager
import json  # Neuer Import für JSON-Verarbeitung

# Create save manager instance
save_mgr = SaveManager()

def handle_input(name):
    # Don't accept commands if player is dead
    if name.is_dead:
        print("\n☠ You are deceased. Game over.")
        return "negative"
        
    # Get the raw user input (without converting to lowercase)
    user_input = input(f"\n[{name.position('dimension')}:{name.position('x')},{name.position('y')}] {name.name} > ")
    
    # Create a lowercase version for command detection only
    command_lower = user_input.lower()
    result = "positive"
    
    if command_lower.startswith("move "):
        parts = user_input.split(" ")
        if len(parts) != 3:
            print("\n✗ Invalid move command. Format: move X Y\n")
            return "positive"
        try:
            x = int(parts[1])
            y = int(parts[2])
            name.move(x,y)
            return "positive"
        except ValueError:
            print("\n✗ Invalid coordinates. Please enter numbers.\n")
            return "positive"
            
    elif command_lower == "whereami":
        dimension = name.position('dimension')
        x_pos = name.position('x')
        y_pos = name.position('y')
        
        print("\n=== CURRENT LOCATION ===")
        print(f"» Dimension: {dimension}")
        print(f"» Coordinates: [{x_pos}, {y_pos}]")
        try:
            dim_title = name.dimension.title
            print(f"» System: {dim_title}")
        except AttributeError:
            pass
        print("=======================\n")
        return "positive"
        
    elif command_lower.startswith("jump "): 
        dimension_name = user_input.split(" ")[1].upper()
        name.jump(dimension_name)
        return "positive"
        
    elif command_lower == "dimensions":
        available = Dimension.get_available_dimensions()
        
        print("\n=== AVAILABLE DIMENSIONS ===")
        for i, dim in enumerate(available):
            try:
                temp_dim = Dimension(dim)
                discovered = dim in name.known_dimensions
                status = "DISCOVERED" if discovered else "UNDISCOVERED"
                
                if discovered:
                    print(f"» {dim}: {temp_dim.title} - {temp_dim.description}")
                else:
                    print(f"» {dim}: {status}")
            except:
                print(f"» {dim}")
        print("===========================\n")
        return "positive"
        
    elif command_lower == "scan":
        try:
            # Scan durchführen
            scan_results = handle_scan(name)
            
            # Entdeckungen dem Spieler erst nach der Anzeige hinzufügen
            # damit der NEW!-Status korrekt angezeigt wird
            current_dimension = name.position('dimension')
            for obj_dict, _ in scan_results:
                # Objekt-Name aus dem Dictionary holen
                obj_name = obj_dict['name']
                
                # Nur neue Objekte mit bekanntem Namen hinzufügen
                if obj_name != 'Unknown':
                    if current_dimension not in name.known_bodies:
                        name.known_bodies[current_dimension] = []
                    if obj_name not in name.known_bodies[current_dimension]:
                        name.known_bodies[current_dimension].append(obj_name)
        except Exception as e:
            print(f"\nScan error: {e}")
        return "positive"
        
    elif command_lower in ["quit", "exit"]:
        # Save before quitting
        save_mgr.save_game(name)
        print("\n=== SYSTEM SHUTDOWN ===")
        print("Saving data... Done!")
        print("Closing connections...")
        print("\nGoodbye Captain! Safe travels.\n")
        return "negative"
        
    elif command_lower == "help":
        display_help()
        return "positive"
        
    elif command_lower == "discoveries":
        display_discoveries(name)
        return "positive"
        
    elif command_lower.startswith("changename "):
        # Extract the new name from command, preserving original case
        parts = user_input.split(" ", 1)
        if len(parts) != 2:
            print("\n✗ Invalid command format. Use: changename YourNewName")
            return "positive"
            
        new_name = parts[1]  # This now preserves the original capitalization
        
        # Attempt to change the player's name
        success, message = save_mgr.change_player_name(name, new_name)
        
        if success:
            print(f"\n✓ {message}")
            print(f"✓ Your unique player ID remains: {name.uuid}")
        else:
            print(f"\n✗ Failed to change name: {message}")
            # Add more detailed error message if name format is invalid
            if "Invalid name format" in message:
                print("  Names must be 3-15 characters long and can contain:")
                print("  - Uppercase letters (A-Z)")
                print("  - Lowercase letters (a-z)")
                print("  - Numbers (0-9)")
                print("  - Underscores (_)")
            
        return "positive"
        
    elif command_lower.startswith("playerinfo"):
        parts = user_input.split(None, 1)  # Split by whitespace, max 1 split
        
        if len(parts) > 1:
            # Check another player by name
            other_player_name = parts[1]
            display_other_player_info(other_player_name)
        else:
            # Save game data first to ensure playtime is accurate
            # Calculate current session playtime and add it to total
            current_time = datetime.datetime.now()
            if hasattr(name, "session_start"):
                session_duration = (current_time - name.session_start).total_seconds()
                name.playtime += session_duration
                # Update session start time for future calculations
                name.session_start = current_time
            
            # Save the updated data
            save_mgr.save_game(name)
            
            # Show current player info
            print("\n=== PLAYER INFORMATION ===")
            print(f"» Name: {name.name}")
            print(f"» UUID: {name.uuid}")
            print(f"» Status: {'Alive' if not name.is_dead else 'Deceased'}")
            print(f"» Current Dimension: {name.dimension.name} ({name.dimension.title})")
            print(f"» Position: [{name.x}, {name.y}]")
            print(f"» Dimensions visited: {len(name.known_dimensions)}")
            
            # Count total discovered bodies
            total_bodies = sum(len(bodies) for bodies in name.known_bodies.values())
            print(f"» Celestial bodies discovered: {total_bodies}")
            
            # Display playtime from player object
            if hasattr(name, "playtime"):
                # Get formatted playtime from save_mgr
                playtime = save_mgr.format_playtime(name.playtime)
                print(f"» Total playtime: {playtime}")
            
            # Display creation date and last login if available
            if hasattr(name, "creation_date"):
                creation_date = format_datetime(name.creation_date)
                print(f"» Created: {creation_date}")
            
            print("=========================\n")
        return "positive"
        
    elif command_lower == "self-destruct":
        print("\n⚠ WARNING: Self-destruct sequence initiated!")
        print("⚠ This will permanently kill your character")
        confirm = input("Type 'CONFIRM' to proceed: ")
        
        if confirm == "CONFIRM":
            result = name.kill()
            save_mgr.save_game(name)  # Save dead status
        else:
            print("Self-destruct sequence aborted.")
        
    elif command_lower == "logout":
        print("\n=== LOGGING OUT ===")
        print("Saving current session...")
        save_mgr.save_game(name)
        print("Session data saved successfully.")
        print("Returning to login screen...")
        return "logout"  # New special return value for logout
        
    else:
        print("\n✗ Unknown command. Type 'help' for available commands.\n")
    
    # Save after every command (only if not already returning "negative" or "logout")
    if result != "negative" and command_lower != "logout":
        save_mgr.save_game(name)
    return result

def handle_scan(player):
    """Scan the nearby area for planets"""
    try:
        # Scan-System aufrufen
        raw_results = scan_system(player)
        
        # Ergebnisse filtern - jetzt mit korrekter Dictionary-Verarbeitung
        filtered_results = []
        for item in raw_results:
            # Die Scan-Ergebnisse sind Dictionaries, keine Tupel
            if isinstance(item, dict) and 'name' in item and 'distance' in item:
                # Daten aus dem Dictionary extrahieren
                name = item['name']
                obj_type = item.get('type', 'Unknown')
                
                # Monde überspringen - Prüfen anhand des Typs, nicht anhand eines is_moon-Attributs
                if obj_type.lower() == 'moon':
                    continue
                
                # Wir verwenden die bereits berechnete Bewegungsdistanz aus scan_system
                movement_distance = item['distance']
                
                # Prüfe, ob das Objekt neu entdeckt wurde
                current_dimension = player.position('dimension')
                is_new_discovery = item.get('new_discovery', False)
                
                # Objekt zur gefilterten Liste hinzufügen
                filtered_results.append((item, movement_distance))
            else:
                print(f"Warning: Unexpected scan result format: {item}")
                continue
        
        # Anzeige der gefilterten Ergebnisse als Tabelle
        if filtered_results:
            print("\n=== SCAN RESULTS ===")
            print(f"Found {len(filtered_results)} celestial bodies:")
            print(f"{'Type':<15} {'Name':<20} {'Coordinates':<20} {'Distance':<10} {'Signals':<10} {'Status':<10}")
            print("-" * 85)
            
            for obj_dict, distance in filtered_results:
                obj_name = obj_dict['name']
                obj_type = obj_dict.get('type', 'Unknown')
                coords = f"({obj_dict['coords'][0]}, {obj_dict['coords'][1]})"
                
                # Format distance as integer (travel time in seconds)
                distance_formatted = f"{int(distance)}s"
                
                # Get signals count (moons + stations)
                signals_count = obj_dict.get('signals_count', 0)
                
                # Set status based on whether it's a new discovery
                status = "NEW!" if obj_dict.get('new_discovery', False) else ""
                
                print(f"{obj_type:<15} {obj_name:<20} {coords:<20} {distance_formatted:<10} {signals_count:<10} {status:<10}")
            
            print("===================\n")
        else:
            print(f"\nNo objects detected in this system.")
        
        return filtered_results
        
    except Exception as e:
        print(f"\nError during scan: {e}")
        import traceback
        traceback.print_exc()
        return []  # Bei einem Fehler eine leere Liste zurückgeben

def display_help(first_time=False):
    print("\n" + "=" * 50)
    print("             COMMAND REFERENCE")
    print("=" * 50)
    
    if first_time:
        print("\n👋 Welcome, new Captain! Here are the commands to get you started:\n")
    
    commands = [
        ("move X Y", "Navigate to coordinates X, Y"),
        ("whereami", "Display current location information"),
        ("jump DIM", "Jump to dimension DIM (e.g. A01, C12)"),
        ("dimensions", "List all available dimensions"),
        ("scan", "Scan current system for celestial bodies"),
        ("discoveries", "Display all your discoveries"),
        ("changename NAME", "Change your captain's name"),
        ("playerinfo [NAME]", "Display player info (yours or another captain)"),
        ("logout", "Save and log out to switch captains"),
        ("self-destruct", "End your journey permanently"),
        ("quit/exit", "Exit the game"),
        ("help", "Display this help message")
    ]
    
    for cmd, desc in commands:
        print(f"» {cmd.ljust(15)} - {desc}")
    
    if first_time:
        print("\n💡 TIP: Start by typing 'scan' to discover nearby celestial bodies")
        print("   or 'dimensions' to see what star systems you can visit!")
    
    print("=" * 50 + "\n")

def display_discoveries(player):
    print("\n" + "=" * 50)
    print("             YOUR DISCOVERIES")
    print("=" * 50)
    
    print(f"\nDimensions visited: {len(player.known_dimensions)}")
    for dim_name in player.known_dimensions:
        try:
            dim = Dimension(dim_name)
            bodies_count = len(player.known_bodies.get(dim_name, []))
            print(f"\n» {dim_name}: {dim.title}")
            print(f"  {dim.description}")
            print(f"  Discovered bodies: {bodies_count}")
            
            if bodies_count > 0:
                for body in player.known_bodies[dim_name]:
                    print(f"   - {body}")
        except:
            print(f"» {dim_name}: [Data corrupted]")
    
    print("\n" + "=" * 50)

def display_other_player_info(player_name):
    """Display information about another player by name"""
    print("\n=== PLAYER INFORMATION ===")
    
    # Get player data from save files
    player_data = None
    for save_file in save_mgr.save_directory.glob('*.json'):
        try:
            with open(save_file, 'r') as f:
                data = json.load(f)
                if data.get("name", "").lower() == player_name.lower():
                    player_data = data
                    break
        except:
            continue
    
    if not player_data:
        print(f"» Captain '{player_name}' not found in records.")
        print("=========================\n")
        return
        
    print(f"» Name: {player_data['name']}")
    
    # Show UUID
    if "uuid" in player_data:
        print(f"» UUID: {player_data['uuid']}")
    
    # Show status (alive/deceased)
    status = "Alive" if not player_data.get("is_dead", False) else "Deceased"
    print(f"» Status: {status}")
    
    # Only show discovery stats if player is not dead
    if not player_data.get("is_dead", False):
        # Show discoveries stats
        try:
            dims_visited = len(player_data["discoveries"]["known_dimensions"])
            print(f"» Dimensions visited: {dims_visited}")
        except:
            print("» Dimensions visited: Unknown")
        
        # Count total bodies
        try:
            known_bodies = player_data["discoveries"]["known_bodies"]
            total_bodies = sum(len(bodies) for bodies in known_bodies.values())
            print(f"» Celestial bodies discovered: {total_bodies}")
        except:
            print("» Celestial bodies discovered: Unknown")
        
        # Show playtime if available in save file
        if "playtime" in player_data:
            # Display the formatted playtime string directly from the save file
            playtime = player_data["playtime"]
            print(f"» Total playtime: {playtime}")
        
        # Show creation date and last login
        if "creation_date" in player_data:
            creation_date = format_datetime(player_data["creation_date"])
            print(f"» Created: {creation_date}")
        
        if "last_login" in player_data:
            last_login = format_datetime(player_data["last_login"])
            print(f"» Last login: {last_login}")
    
    print("=========================\n")

def format_datetime(iso_date_str):
    """Format ISO date string to DD.MM.YY - HH:MM format using Berlin timezone"""
    try:
        dt = datetime.datetime.fromisoformat(iso_date_str)
        
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
            
        return dt.strftime("%d.%m.%y - %H:%M")
    except:
        return iso_date_str  # Return the original string if parsing fails