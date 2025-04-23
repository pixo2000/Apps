import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import threading
import time
import socket
import json

class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Application")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        self.server_url = "http://localhost:80"  # Change this to your server address
        self.user_id = None
        self.username = None
        self.computer_name = socket.gethostname()
        self.message_count = 0
        self.polling = False
        
        self.create_login_frame()
    
    def create_login_frame(self):
        self.login_frame = ttk.Frame(self.root, padding=20)
        self.login_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(self.login_frame, text="Chat Application", font=("Arial", 18, "bold")).pack(pady=10)
        
        self.username_frame = ttk.Frame(self.login_frame)
        self.username_frame.pack(pady=20, fill=tk.X)
        
        ttk.Label(self.username_frame, text="Username:").pack(side=tk.LEFT, padx=5)
        self.username_entry = ttk.Entry(self.username_frame, width=30)
        self.username_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.username_entry.focus()
        
        self.login_button = ttk.Button(self.login_frame, text="Login / Register", command=self.register_user)
        self.login_button.pack(pady=10)
        
        self.status_label = ttk.Label(self.login_frame, text="")
        self.status_label.pack(pady=5)
        
        # Bind Enter key to login button
        self.username_entry.bind("<Return>", lambda event: self.register_user())
    
    def create_chat_frame(self):
        self.chat_frame = ttk.Frame(self.root, padding=10)
        self.chat_frame.pack(fill=tk.BOTH, expand=True)
        
        # Top info bar
        self.info_frame = ttk.Frame(self.chat_frame)
        self.info_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(self.info_frame, text=f"Logged in as: {self.username} ({self.computer_name})").pack(side=tk.LEFT)
        self.logout_button = ttk.Button(self.info_frame, text="Logout", command=self.logout)
        self.logout_button.pack(side=tk.RIGHT)
        
        # Split view with users list and chat
        self.paned_window = ttk.PanedWindow(self.chat_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Users list
        self.users_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.users_frame, weight=1)
        
        ttk.Label(self.users_frame, text="Online Users").pack(fill=tk.X)
        self.users_list = tk.Listbox(self.users_frame)
        self.users_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Chat area
        self.messages_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.messages_frame, weight=3)
        
        # Messages display
        self.messages_display = scrolledtext.ScrolledText(self.messages_frame, state=tk.DISABLED)
        self.messages_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Message input
        self.input_frame = ttk.Frame(self.chat_frame)
        self.input_frame.pack(fill=tk.X, pady=10)
        
        self.message_entry = ttk.Entry(self.input_frame)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.send_button = ttk.Button(self.input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT)
        
        # Bind Enter key to send button
        self.message_entry.bind("<Return>", lambda event: self.send_message())
    
    def register_user(self):
        username = self.username_entry.get().strip()
        
        if not username:
            messagebox.showerror("Error", "Username cannot be empty")
            return
        
        try:
            response = requests.post(
                f"{self.server_url}/api/register",
                json={
                    "username": username,
                    "computer_name": self.computer_name
                }
            )
            
            data = response.json()
            
            if response.status_code == 200 and data.get('status') == 'success':
                self.user_id = data.get('user_id')
                self.username = data.get('username')
                
                # Clear login frame and create chat frame
                self.login_frame.destroy()
                self.create_chat_frame()
                
                # Start polling for messages
                self.polling = True
                self.poll_thread = threading.Thread(target=self.poll_messages, daemon=True)
                self.poll_thread.start()
                
                self.users_thread = threading.Thread(target=self.poll_users, daemon=True)
                self.users_thread.start()
            else:
                messagebox.showerror("Error", data.get('message', 'Failed to register'))
        
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")
    
    def send_message(self):
        message = self.message_entry.get().strip()
        
        if not message:
            return
        
        try:
            response = requests.post(
                f"{self.server_url}/api/send_message",
                json={
                    "user_id": self.user_id,
                    "content": message
                }
            )
            
            data = response.json()
            
            if response.status_code == 200 and data.get('status') == 'success':
                self.message_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Error", data.get('message', 'Failed to send message'))
        
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")
    
    def poll_messages(self):
        while self.polling:
            try:
                response = requests.get(
                    f"{self.server_url}/api/get_messages",
                    params={
                        "user_id": self.user_id,
                        "since": self.message_count
                    }
                )
                
                data = response.json()
                
                if response.status_code == 200 and data.get('status') == 'success':
                    new_messages = data.get('messages', [])
                    self.message_count = data.get('message_count', self.message_count)
                    
                    for message in new_messages:
                        self.display_message(message)
            
            except Exception as e:
                print(f"Error polling messages: {str(e)}")
            
            time.sleep(1)
    
    def poll_users(self):
        while self.polling:
            try:
                response = requests.get(
                    f"{self.server_url}/api/get_users",
                    params={"user_id": self.user_id}
                )
                
                data = response.json()
                
                if response.status_code == 200 and data.get('status') == 'success':
                    users = data.get('users', [])
                    
                    self.users_list.delete(0, tk.END)
                    for user in users:
                        self.users_list.insert(tk.END, f"{user['username']} ({user['computer_name']})")
            
            except Exception as e:
                print(f"Error polling users: {str(e)}")
            
            time.sleep(5)  # Update user list every 5 seconds
    
    def display_message(self, message):
        self.messages_display.config(state=tk.NORMAL)
        timestamp = message.get('timestamp', '').split('T')[1].split('.')[0]  # Extract time portion
        sender_name = message.get('sender_name', 'Unknown')
        computer_name = message.get('computer_name', 'Unknown')
        content = message.get('content', '')
        
        formatted_message = f"[{timestamp}] {sender_name} ({computer_name}): {content}\n"
        self.messages_display.insert(tk.END, formatted_message)
        self.messages_display.see(tk.END)  # Scroll to the end
        self.messages_display.config(state=tk.DISABLED)
    
    def logout(self):
        self.polling = False
        self.user_id = None
        self.username = None
        
        # Clear chat frame and create login frame
        self.chat_frame.destroy()
        self.create_login_frame()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClient(root)
    root.mainloop()
