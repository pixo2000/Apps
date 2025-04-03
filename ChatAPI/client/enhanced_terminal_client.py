import os
import sys
import threading
import time
import argparse
import readline
from datetime import datetime
from socketclient import WebSocketClient

class EnhancedTerminalChat:
    def __init__(self, server_url="http://localhost", port=5500):
        self.server_url = server_url
        self.port = port
        self.username = "Anonymous"
        self.client = WebSocketClient(server_url, port)
        self.client.register_message_callback(self.handle_new_messages)
        self.running = False
        self.message_buffer = []
        self.max_messages = 20  # Maximum messages to show on screen
        self.lock = threading.Lock()
        
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def refresh_display(self):
        """Refresh the entire display."""
        self.clear_screen()
        self.draw_header()
        self.draw_messages()
        self.draw_input_prompt()
        
    def draw_header(self):
        """Draw the header of the chat interface."""
        width = os.get_terminal_size().columns
        print("=" * width)
        header = f" WebSocket Chat - Server: {self.server_url}:{self.port} - User: {self.username} "
        padding = (width - len(header)) // 2
        print(" " * padding + header)
        print("=" * width)
        print(" Commands: /quit - Exit   /username <name> - Change username   /clear - Clear screen")
        print("-" * width)
        
    def draw_messages(self):
        """Draw the message area with scrolling."""
        # Only display the last N messages to fit the screen
        display_messages = self.message_buffer[-self.max_messages:] if len(self.message_buffer) > self.max_messages else self.message_buffer
        
        for msg in display_messages:
            print(f"[{msg['timestamp']}] {msg['username']}: {msg['message']}")
            
        # Add empty lines if there aren't enough messages
        if len(display_messages) < self.max_messages:
            print("\n" * (self.max_messages - len(display_messages)), end="")
            
        print("-" * os.get_terminal_size().columns)
        
    def draw_input_prompt(self):
        """Draw the input prompt."""
        sys.stdout.write("> ")
        sys.stdout.flush()
        
    def handle_new_messages(self, messages):
        """Process new incoming messages."""
        with self.lock:
            for msg in messages:
                self.message_buffer.append(msg)
            self.refresh_display()
            
    def process_command(self, command):
        """Process a user command."""
        if command.lower() == "/quit":
            self.running = False
            return True
        elif command.lower().startswith("/username "):
            new_username = command[10:].strip()
            if new_username:
                self.username = new_username
                self.client.set_username(new_username)
                self.add_system_message(f"Username changed to: {new_username}")
            return True
        elif command.lower() == "/clear":
            self.message_buffer = []
            self.refresh_display()
            return True
        return False
        
    def add_system_message(self, text):
        """Add a system message to the chat."""
        system_msg = {
            'username': 'System',
            'message': text,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
        self.message_buffer.append(system_msg)
        self.refresh_display()
        
    def input_loop(self):
        """Handle user input in a loop."""
        while self.running:
            try:
                user_input = input("> ")
                # Clear the input line
                sys.stdout.write('\033[1A\033[2K')
                
                # If it's a command, process it
                if user_input.startswith('/'):
                    if self.process_command(user_input):
                        continue
                
                # Otherwise send as a message
                if user_input.strip():
                    if not self.client.send_message(user_input):
                        self.add_system_message("Failed to send message. Check your connection.")
                        
            except KeyboardInterrupt:
                self.running = False
                break
            except Exception as e:
                self.add_system_message(f"Error: {str(e)}")
                
    def run(self):
        """Start the chat client."""
        print(f"Connecting to {self.server_url}:{self.port}...")
        if not self.client.connect_to_server():
            print("Failed to connect to the server.")
            return
            
        self.client.set_username(self.username)
        self.running = True
        self.add_system_message(f"Connected to {self.server_url}:{self.port}")
        
        # Get message history
        self.client.get_message_history()
        
        # Start the main input loop
        self.input_loop()
        
        # Clean up when done
        print("\nDisconnecting...")
        self.client.disconnect()
        
def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Enhanced Terminal WebSocket Chat Client")
    parser.add_argument("-s", "--server", default="http://localhost", 
                        help="Server URL (default: http://localhost)")
    parser.add_argument("-p", "--port", type=int, default=5500, 
                        help="Server port (default: 5500)")
    parser.add_argument("-u", "--username", default="Anonymous",
                        help="Username (default: Anonymous)")
    
    args = parser.parse_args()
    
    # Create and start the client
    client = EnhancedTerminalChat(args.server, args.port)
    client.username = args.username
    
    try:
        client.run()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {str(e)}")
    
if __name__ == "__main__":
    main()
