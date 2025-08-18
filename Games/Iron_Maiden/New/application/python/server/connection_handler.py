# import other files
import sys
sys.path.append('..')
from player import Player

# import modules
import threading
import pickle

class ConnectionHandler:
    def __init__(self):
        self.players = []
        self.player_connections = []
        self.lock = threading.Lock()

    def handle_client(self, conn, addr, battle_handler):
        player = None
        try:
            # Receive player data
            player_data = pickle.loads(conn.recv(1024))
            player = Player(player_data['name'], player_data['team'], (0, 0))
            
            with self.lock:
                self.players.append(player)
                self.player_connections.append(conn)
                
                # If we have 2 players, start the battle
                if len(self.players) == 2:
                    battle_handler.start_battle(self.players, self.player_connections)
                    
            # Wait for battle commands
            while True:
                try:
                    data = conn.recv(1024)
                    if not data:
                        print(f"Client {addr} disconnected")
                        break
                        
                    command = pickle.loads(data)
                    battle_handler.handle_battle_command(command, player, self.players, self.player_connections)
                except ConnectionResetError:
                    print(f"Client {addr} connection was reset")
                    break
                except ConnectionAbortedError:
                    print(f"Client {addr} connection was aborted")
                    break
                except Exception as e:
                    print(f"Error handling client {addr}: {e}")
                    break
                    
        except Exception as e:
            print(f"Error handling client {addr}: {e}")
        finally:
            with self.lock:
                if player and player in self.players:
                    self.players.remove(player)
                if conn in self.player_connections:
                    self.player_connections.remove(conn)
                try:
                    conn.close()
                except:
                    pass
            print(f"Client {addr} cleanup completed")
            conn.close()