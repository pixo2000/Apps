import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
from main import ChatClient

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Application")
        self.root.geometry("600x700")
        
        # Create the chat client
        self.client = ChatClient()
        
        # Create frames
        self.setup_ui()
        
        # Start message polling
        self.poll_thread = threading.Thread(target=self.poll_messages, daemon=True)
        self.poll_thread.start()
        
    def setup_ui(self):
        # Connection frame
        connection_frame = ttk.LabelFrame(self.root, text="Server Connection")
        connection_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(connection_frame, text="Server URL:").grid(row=0, column=0, padx=5, pady=5)
        self.server_url = ttk.Entry(connection_frame)
        self.server_url.insert(0, "http://localhost")
        self.server_url.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(connection_frame, text="Port:").grid(row=0, column=2, padx=5, pady=5)
        self.server_port = ttk.Entry(connection_frame, width=6)
        self.server_port.insert(0, "80")
        self.server_port.grid(row=0, column=3, padx=5, pady=5)
        
        self.connect_button = ttk.Button(connection_frame, text="Connect", command=self.connect_to_server)
        self.connect_button.grid(row=0, column=4, padx=5, pady=5)
        
        # Username frame
        username_frame = ttk.LabelFrame(self.root, text="Your Identity")
        username_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(username_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5)
        self.username_entry = ttk.Entry(username_frame)
        self.username_entry.insert(0, "Anonymous")
        self.username_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        self.set_username_button = ttk.Button(username_frame, text="Set Username", command=self.set_username)
        self.set_username_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Chat display
        chat_frame = ttk.LabelFrame(self.root, text="Chat Messages")
        chat_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.chat_display = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, state='disabled')
        self.chat_display.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Input frame
        input_frame = ttk.Frame(self.root)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        self.message_input = ttk.Entry(input_frame)
        self.message_input.pack(fill="x", side="left", expand=True, padx=(0, 5))
        self.message_input.bind("<Return>", lambda event: self.send_message())
        
        self.send_button = ttk.Button(input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side="right")
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Disconnected")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w")
        self.status_bar.pack(fill="x", side="bottom", padx=10, pady=5)
        
        # Configure grid weights
        connection_frame.columnconfigure(1, weight=1)
        username_frame.columnconfigure(1, weight=1)
    
    def connect_to_server(self):
        url = self.server_url.get()
        try:
            port = int(self.server_port.get())
        except ValueError:
            messagebox.showerror("Invalid Port", "Please enter a valid port number")
            return
        
        self.client = ChatClient(url, port)
        if self.client.check_server():
            self.status_var.set(f"Connected to {url}:{port}")
            messagebox.showinfo("Connection Successful", "Connected to the chat server!")
        else:
            self.status_var.set("Failed to connect")
            messagebox.showerror("Connection Failed", "Could not connect to the server")
    
    def set_username(self):
        username = self.username_entry.get()
        if username:
            self.client.set_username(username)
            messagebox.showinfo("Username Set", f"Your username is now: {username}")
        else:
            messagebox.showerror("Invalid Username", "Username cannot be empty")
    
    def send_message(self):
        message = self.message_input.get()
        if not message:
            return
        
        success = self.client.send_message(message)
        if success:
            self.message_input.delete(0, tk.END)
        else:
            messagebox.showerror("Send Failed", "Failed to send message")
    
    def poll_messages(self):
        while True:
            try:
                if hasattr(self, 'client'):
                    new_messages = self.client.get_new_messages()
                    if new_messages:
                        self.update_chat_display(new_messages)
            except Exception as e:
                print(f"Error polling messages: {e}")
            time.sleep(1)
    
    def update_chat_display(self, messages):
        self.chat_display.config(state='normal')
        for msg in messages:
            formatted_msg = f"[{msg['timestamp']}] {msg['username']}: {msg['message']}\n"
            self.chat_display.insert(tk.END, formatted_msg)
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)  # Auto-scroll to the bottom

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
