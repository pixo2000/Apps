import os
import sys
import threading
import time
import argparse
from socketclient import WebSocketClient

class TerminalChatClient:
    def __init__(self, server_url="http://localhost", port=5500):
        self.server_url = server_url
        self.port = port
        self.username = "Anonymous"
        self.client = WebSocketClient(server_url, port)
        self.client.register_message_callback(self.display_message)
        self.running = False
        self.last_message_count = 0
        
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def print_header(self):
        """Print the chat header."""
        print("=" * 60)
        print(f"  WebSocket Chat Terminal Client - Connected to {self.server_url}:{self.port}")
        print(f"  Username: {self.username}")
        print("=" * 60)
        print("Type your message and press Enter to send. Type /quit to exit.")
        print("Type /username <new_name> to change your username.")
        print("-" * 60)
        
    def display_message(self, messages):
        """Callback to display new messages."""
        for msg in messages:
            # Print message without disrupting input line
            sys.stdout.write(f"\r[{msg['timestamp']}] {msg['username']}: {msg['message']}\n> ")
            sys.stdout.flush()
            
    def input_loop(self):
        """Handle user input in a loop."""
        while self.running:
            try:
                user_input = input("> ")
                
                # Handle commands
                if user_input.lower() == "/quit":
                    self.running = False
                    print("Disconnecting...")
                    break
                elif user_input.lower().startswith("/username "):
                    new_username = user_input[10:].strip()
                    if new_username:
                        self.username = new_username
                        self.client.set_username(new_username)
                        print(f"Username changed to: {new_username}")
                # Send regular message
                elif user_input.strip():
                    if not self.client.send_message(user_input):
                        print("Failed to send message. Check your connection.")
            except KeyboardInterrupt:
                self.running = False
                break
            except Exception as e:
                print(f"Error: {e}")
                
    def connect(self):
        """Connect to the chat server."""
        print(f"Connecting to {self.server_url}:{self.port}...")
        if self.client.connect_to_server():
            self.client.set_username(self.username)
            self.running = True
            
            # Clear screen and show header
            self.clear_screen()
            self.print_header()
            
            # Get message history
            self.client.get_message_history()
            
            # Start input loop in the main thread
            self.input_loop()
            
            # Disconnect when done
            self.client.disconnect()
            print("Disconnected from server.")
        else:
            print("Failed to connect to the server.")
            
def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Terminal WebSocket Chat Client")
    parser.add_argument("-s", "--server", default="http://localhost", 
                        help="Server URL (default: http://localhost)")
    parser.add_argument("-p", "--port", type=int, default=5500, 
                        help="Server port (default: 5500)")
    parser.add_argument("-u", "--username", default="Anonymous",
                        help="Username (default: Anonymous)")
    
    args = parser.parse_args()
    
    # Create and start the client
    client = TerminalChatClient(args.server, args.port)
    client.username = args.username
    
    try:
        client.connect()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
    
if __name__ == "__main__":
    main()
