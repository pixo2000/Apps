# import other files
from player import Player

# import modules
import socket
import pickle
import threading
import sys
import json
import os

# Load configuration
with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'r') as config_file:
    config = json.load(config_file)
    server_port = config['server-port']
    server_ip = config['server-ip']

def receive_messages(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("\nServer connection closed")
                break
                
            message = pickle.loads(data)
            
            if message['type'] == 'battle_start':
                print("\nBattle is starting!")
                for p in message['players']:
                    print(f"{p['name']}: Health={p['health']}, Attack={p['attack']}")
                print("\nType 'attack' to attack your opponent!")
                
            elif message['type'] == 'battle_update':
                print(f"\n{message['attacker']} attacked {message['defender']}!")
                print(f"{message['defender']} health: {message['defender_health']}")
                
            elif message['type'] == 'game_over':
                print(f"\nGame Over! {message['winner']} wins!")
                print("Press Enter to exit...")
                sys.exit(0)
                
        except ConnectionResetError:
            print("\nServer connection was forcibly closed")
            break
        except ConnectionAbortedError:
            print("\nServer connection was aborted")
            break
        except Exception as e:
            print(f"\nError receiving message: {e}")
            break
    
    print("\nDisconnected from server")
    sys.exit(1)

# main loop
def main():
    print("Welcome to the Battle Game!")
    name = input("Enter your name: ")
    team = input("Enter your team: ")
    
    # Connect to server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((server_ip, server_port))
    except:
        print("Could not connect to server")
        print(server_ip, server_port)
        return
        
    # Send player info
    player_data = {
        'name': name,
        'team': team
    }
    client.send(pickle.dumps(player_data))
    
    # Start receiving messages
    thread = threading.Thread(target=receive_messages, args=(client,))
    thread.daemon = True
    thread.start()
    
    print("\nWaiting for another player to join...")
    
    # Main game loop
    try:
        while True:
            command = input()
            if command.lower() == 'attack':
                battle_command = {
                    'action': 'attack'
                }
                client.send(pickle.dumps(battle_command))
    except KeyboardInterrupt:
        print("\nDisconnecting...")
    finally:
        client.close()

# yeah lol
if __name__ == "__main__":
    main()