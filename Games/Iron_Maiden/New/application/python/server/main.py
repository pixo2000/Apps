# import other files
import sys
sys.path.append('..')
from player import Player
from connection_handler import ConnectionHandler
from battle_handler import BattleHandler

# import modules
import json
import os
import socket
import threading

# Load configuration
with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'r') as config_file:
    config = json.load(config_file)
    port = config['port']

# main loop
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', port))
    server.listen(2)
    print(f"Server started on port {port}")
    
    connection_handler = ConnectionHandler()
    battle_handler = BattleHandler()
    
    try:
        while True:
            conn, addr = server.accept()
            print(f"New connection from {addr}")
            thread = threading.Thread(
                target=connection_handler.handle_client,
                args=(conn, addr, battle_handler)
            )
            thread.start()
    except KeyboardInterrupt:
        print("Server shutting down...")
    finally:
        server.close()

if __name__ == "__main__":
    main()