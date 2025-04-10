import requests
import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from functools import partial

BASE_URL = "http://localhost:5000/api"

class LoginAPIClient:
    def __init__(self):
        self.token = None
        self.user_data = None
    
    def register(self, name, email, password):
        """Register a new user"""
        url = f"{BASE_URL}/register"
        data = {
            "name": name,
            "email": email,
            "password": password
        }
        response = requests.post(url, json=data)
        return self._handle_response(response)
    
    def login(self, email, password):
        """Login and get authentication token"""
        url = f"{BASE_URL}/login"
        data = {
            "email": email,
            "password": password
        }
        response = requests.post(url, json=data)
        result = self._handle_response(response)
        
        if result["success"]:
            self.token = result["data"]["token"]
            self.user_data = result["data"]["user"]
        
        return result
    
    def get_profile(self):
        """Get user profile"""
        if not self.token:
            return {"success": False, "message": "Not logged in"}
        
        url = f"{BASE_URL}/user"
        headers = self._get_auth_header()
        response = requests.get(url, headers=headers)
        return self._handle_response(response)
    
    def update_profile(self, name=None, email=None, password=None):
        """Update user profile"""
        if not self.token:
            return {"success": False, "message": "Not logged in"}
        
        url = f"{BASE_URL}/user"
        data = {}
        if name:
            data["name"] = name
        if email:
            data["email"] = email
        if password:
            data["password"] = password
        
        headers = self._get_auth_header()
        response = requests.put(url, json=data, headers=headers)
        return self._handle_response(response)
    
    def request_password_reset(self, email):
        """Request password reset email"""
        url = f"{BASE_URL}/password-reset-request"
        data = {"email": email}
        response = requests.post(url, json=data)
        return self._handle_response(response)
    
    def reset_password(self, token, new_password):
        """Reset password using token"""
        url = f"{BASE_URL}/password-reset/{token}"
        data = {"password": new_password}
        response = requests.post(url, json=data)
        return self._handle_response(response)
    
    def get_all_users(self):
        """Admin function to get all users"""
        if not self.token:
            return {"success": False, "message": "Not logged in"}
        
        url = f"{BASE_URL}/admin/users"
        headers = self._get_auth_header()
        response = requests.get(url, headers=headers)
        return self._handle_response(response)
    
    def logout(self):
        """Logout user by clearing token"""
        self.token = None
        self.user_data = None
        return {"success": True, "message": "Logged out successfully"}
    
    def _get_auth_header(self):
        """Get authorization header with token"""
        return {"x-access-token": self.token}
    
    def _handle_response(self, response):
        """Handle API response"""
        try:
            data = response.json()
            if response.status_code >= 200 and response.status_code < 300:
                return {"success": True, "data": data}
            else:
                message = data.get("message", "Unknown error")
                return {"success": False, "message": message, "status_code": response.status_code}
        except:
            return {"success": False, "message": "Could not parse response", "status_code": response.status_code}


class LoginAPIGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Login API Client")
        self.client = LoginAPIClient()
        
        # Set window size and center it
        width = 800
        height = 600
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        self.root.geometry(f'{width}x{height}+{int(x)}+{int(y)}')
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Create tabs
        self.auth_frame = ttk.Frame(self.notebook)
        self.profile_frame = ttk.Frame(self.notebook)
        self.reset_frame = ttk.Frame(self.notebook)
        self.admin_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.auth_frame, text="Login/Register")
        self.notebook.add(self.profile_frame, text="Profile")
        self.notebook.add(self.reset_frame, text="Password Reset")
        self.notebook.add(self.admin_frame, text="Admin")
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief="sunken", anchor="w")
        self.status_bar.pack(side="bottom", fill="x")
        self.status_var.set("Ready")
        
        # Initialize tabs
        self.init_auth_tab()
        self.init_profile_tab()
        self.init_reset_tab()
        self.init_admin_tab()
        
        # Update UI state
        self.update_ui_state()

    def init_auth_tab(self):
        """Initialize Authentication tab (Login/Register)"""
        # Login Frame
        login_frame = ttk.LabelFrame(self.auth_frame, text="Login")
        login_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ttk.Label(login_frame, text="Email:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.login_email = ttk.Entry(login_frame, width=40)
        self.login_email.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(login_frame, text="Password:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.login_password = ttk.Entry(login_frame, width=40, show="*")
        self.login_password.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        login_btn = ttk.Button(login_frame, text="Login", command=self.login)
        login_btn.grid(row=2, column=1, sticky="e", padx=5, pady=10)
        
        # Register Frame
        register_frame = ttk.LabelFrame(self.auth_frame, text="Register New User")
        register_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ttk.Label(register_frame, text="Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.register_name = ttk.Entry(register_frame, width=40)
        self.register_name.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(register_frame, text="Email:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.register_email = ttk.Entry(register_frame, width=40)
        self.register_email.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(register_frame, text="Password:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.register_password = ttk.Entry(register_frame, width=40, show="*")
        self.register_password.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        
        register_btn = ttk.Button(register_frame, text="Register", command=self.register)
        register_btn.grid(row=3, column=1, sticky="e", padx=5, pady=10)

    def init_profile_tab(self):
        """Initialize Profile tab"""
        # Profile info frame
        profile_info_frame = ttk.LabelFrame(self.profile_frame, text="User Profile")
        profile_info_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.profile_info_text = scrolledtext.ScrolledText(profile_info_frame, height=10, width=70)
        self.profile_info_text.pack(padx=10, pady=10, fill="both", expand=True)
        self.profile_info_text.config(state="disabled")
        
        refresh_btn = ttk.Button(profile_info_frame, text="Refresh Profile", command=self.fetch_profile)
        refresh_btn.pack(side="right", padx=5, pady=5)
        
        # Update profile frame
        update_frame = ttk.LabelFrame(self.profile_frame, text="Update Profile")
        update_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ttk.Label(update_frame, text="Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.update_name = ttk.Entry(update_frame, width=40)
        self.update_name.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(update_frame, text="Email:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.update_email = ttk.Entry(update_frame, width=40)
        self.update_email.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(update_frame, text="New Password:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.update_password = ttk.Entry(update_frame, width=40, show="*")
        self.update_password.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        
        update_btn = ttk.Button(update_frame, text="Update Profile", command=self.update_profile)
        update_btn.grid(row=3, column=1, sticky="e", padx=5, pady=10)
        
        # Logout button at bottom
        self.logout_btn = ttk.Button(self.profile_frame, text="Logout", command=self.logout)
        self.logout_btn.pack(side="right", padx=10, pady=10)

    def init_reset_tab(self):
        """Initialize Password Reset tab"""
        # Request reset frame
        request_frame = ttk.LabelFrame(self.reset_frame, text="Request Password Reset")
        request_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ttk.Label(request_frame, text="Email:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.reset_email = ttk.Entry(request_frame, width=40)
        self.reset_email.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        request_btn = ttk.Button(request_frame, text="Request Reset", command=self.request_reset)
        request_btn.grid(row=1, column=1, sticky="e", padx=5, pady=10)
        
        # Reset with token frame
        token_frame = ttk.LabelFrame(self.reset_frame, text="Reset Password with Token")
        token_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ttk.Label(token_frame, text="Reset Token:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.reset_token = ttk.Entry(token_frame, width=40)
        self.reset_token.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(token_frame, text="New Password:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.new_password = ttk.Entry(token_frame, width=40, show="*")
        self.new_password.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        reset_btn = ttk.Button(token_frame, text="Reset Password", command=self.reset_password)
        reset_btn.grid(row=2, column=1, sticky="e", padx=5, pady=10)
        
        # Response area
        response_frame = ttk.LabelFrame(self.reset_frame, text="Response")
        response_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.reset_response = scrolledtext.ScrolledText(response_frame, height=5, width=70)
        self.reset_response.pack(padx=10, pady=10, fill="both", expand=True)
        self.reset_response.config(state="disabled")

    def init_admin_tab(self):
        """Initialize Admin tab"""
        # Admin controls
        admin_control_frame = ttk.Frame(self.admin_frame)
        admin_control_frame.pack(fill="x", padx=10, pady=10)
        
        fetch_users_btn = ttk.Button(admin_control_frame, text="Fetch All Users", command=self.fetch_users)
        fetch_users_btn.pack(side="right")
        
        # Users list
        users_frame = ttk.LabelFrame(self.admin_frame, text="Users")
        users_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create Treeview
        columns = ('name', 'email', 'admin', 'registered_on')
        self.users_tree = ttk.Treeview(users_frame, columns=columns, show='headings')
        
        # Define headings
        self.users_tree.heading('name', text='Name')
        self.users_tree.heading('email', text='Email')
        self.users_tree.heading('admin', text='Admin')
        self.users_tree.heading('registered_on', text='Registered On')
        
        # Column widths
        self.users_tree.column('name', width=150)
        self.users_tree.column('email', width=200)
        self.users_tree.column('admin', width=50)
        self.users_tree.column('registered_on', width=150)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(users_frame, orient="vertical", command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        self.users_tree.pack(fill="both", expand=True)

    def update_ui_state(self):
        """Update UI based on login status"""
        is_logged_in = self.client.token is not None
        
        # Enable or disable profile tab
        if is_logged_in:
            self.notebook.tab(1, state="normal")
            self.notebook.tab(3, state="normal" if self.client.user_data and self.client.user_data.get("admin") else "disabled")
            self.status_var.set(f"Logged in as {self.client.user_data['name']}")
        else:
            self.notebook.tab(1, state="disabled")
            self.notebook.tab(3, state="disabled")
            self.status_var.set("Not logged in")

    def register(self):
        """Register a new user"""
        name = self.register_name.get()
        email = self.register_email.get()
        password = self.register_password.get()
        
        if not name or not email or not password:
            messagebox.showerror("Error", "All fields are required")
            return
        
        self.status_var.set("Registering...")
        
        # Run in a separate thread to keep UI responsive
        def register_thread():
            result = self.client.register(name, email, password)
            if result["success"]:
                self.register_name.delete(0, tk.END)
                self.register_email.delete(0, tk.END)
                self.register_password.delete(0, tk.END)
                messagebox.showinfo("Success", "Registration successful. You can now log in.")
                self.status_var.set("Registration successful")
            else:
                messagebox.showerror("Error", result.get("message", "Registration failed"))
                self.status_var.set("Registration failed")
        
        threading.Thread(target=register_thread).start()

    def login(self):
        """Log in with email and password"""
        email = self.login_email.get()
        password = self.login_password.get()
        
        if not email or not password:
            messagebox.showerror("Error", "Email and password are required")
            return
        
        self.status_var.set("Logging in...")
        
        def login_thread():
            result = self.client.login(email, password)
            if result["success"]:
                self.login_password.delete(0, tk.END)
                self.update_ui_state()
                self.notebook.select(1)  # Switch to profile tab
                self.fetch_profile()
                self.status_var.set(f"Logged in as {self.client.user_data['name']}")
            else:
                messagebox.showerror("Error", result.get("message", "Login failed"))
                self.status_var.set("Login failed")
        
        threading.Thread(target=login_thread).start()

    def logout(self):
        """Log out user"""
        result = self.client.logout()
        if result["success"]:
            self.profile_info_text.config(state="normal")
            self.profile_info_text.delete(1.0, tk.END)
            self.profile_info_text.config(state="disabled")
            self.update_name.delete(0, tk.END)
            self.update_email.delete(0, tk.END)
            self.update_password.delete(0, tk.END)
            self.update_ui_state()
            self.notebook.select(0)  # Switch to login tab
            messagebox.showinfo("Success", "Logged out successfully")
        else:
            messagebox.showerror("Error", result.get("message", "Logout failed"))

    def fetch_profile(self):
        """Fetch and display user profile"""
        if not self.client.token:
            messagebox.showerror("Error", "Not logged in")
            return
            
        self.status_var.set("Fetching profile...")
        
        def fetch_thread():
            result = self.client.get_profile()
            if result["success"]:
                # Update profile info text
                self.profile_info_text.config(state="normal")
                self.profile_info_text.delete(1.0, tk.END)
                self.profile_info_text.insert(tk.END, json.dumps(result["data"], indent=2))
                self.profile_info_text.config(state="disabled")
                
                # Pre-fill update form
                self.update_name.delete(0, tk.END)
                self.update_name.insert(0, result["data"].get("name", ""))
                self.update_email.delete(0, tk.END)
                self.update_email.insert(0, result["data"].get("email", ""))
                
                self.status_var.set("Profile fetched")
            else:
                messagebox.showerror("Error", result.get("message", "Failed to fetch profile"))
                self.status_var.set("Failed to fetch profile")
        
        threading.Thread(target=fetch_thread).start()

    def update_profile(self):
        """Update user profile"""
        if not self.client.token:
            messagebox.showerror("Error", "Not logged in")
            return
            
        name = self.update_name.get()
        email = self.update_email.get()
        password = self.update_password.get()
        
        if not name and not email and not password:
            messagebox.showerror("Error", "At least one field must be filled")
            return
        
        self.status_var.set("Updating profile...")
        
        def update_thread():
            result = self.client.update_profile(name, email, password)
            if result["success"]:
                self.update_password.delete(0, tk.END)
                messagebox.showinfo("Success", "Profile updated successfully")
                self.fetch_profile()
                self.status_var.set("Profile updated")
            else:
                messagebox.showerror("Error", result.get("message", "Failed to update profile"))
                self.status_var.set("Failed to update profile")
        
        threading.Thread(target=update_thread).start()

    def request_reset(self):
        """Request password reset"""
        email = self.reset_email.get()
        
        if not email:
            messagebox.showerror("Error", "Email is required")
            return
        
        self.status_var.set("Requesting password reset...")
        
        def request_thread():
            result = self.client.request_password_reset(email)
            
            # Enable and clear response area
            self.reset_response.config(state="normal")
            self.reset_response.delete(1.0, tk.END)
            
            if result["success"]:
                # Show the response which might contain token in dev mode
                self.reset_response.insert(tk.END, json.dumps(result["data"], indent=2))
                
                # If there's a token in the response, pre-fill the token field
                if "token" in result["data"]:
                    self.reset_token.delete(0, tk.END)
                    self.reset_token.insert(0, result["data"]["token"])
                
                self.status_var.set("Password reset requested")
            else:
                self.reset_response.insert(tk.END, f"Error: {result.get('message', 'Failed to request password reset')}")
                self.status_var.set("Failed to request password reset")
            
            self.reset_response.config(state="disabled")
        
        threading.Thread(target=request_thread).start()

    def reset_password(self):
        """Reset password with token"""
        token = self.reset_token.get()
        password = self.new_password.get()
        
        if not token or not password:
            messagebox.showerror("Error", "Token and new password are required")
            return
        
        self.status_var.set("Resetting password...")
        
        def reset_thread():
            result = self.client.reset_password(token, password)
            
            # Enable and clear response area
            self.reset_response.config(state="normal")
            self.reset_response.delete(1.0, tk.END)
            
            if result["success"]:
                self.reset_response.insert(tk.END, "Password reset successfully. You can now log in with the new password.")
                self.reset_token.delete(0, tk.END)
                self.new_password.delete(0, tk.END)
                self.status_var.set("Password reset successful")
            else:
                self.reset_response.insert(tk.END, f"Error: {result.get('message', 'Failed to reset password')}")
                self.status_var.set("Failed to reset password")
            
            self.reset_response.config(state="disabled")
        
        threading.Thread(target=reset_thread).start()

    def fetch_users(self):
        """Fetch all users (admin only)"""
        if not self.client.token:
            messagebox.showerror("Error", "Not logged in")
            return
        
        self.status_var.set("Fetching users...")
        
        def fetch_thread():
            result = self.client.get_all_users()
            
            # Clear existing users
            for item in self.users_tree.get_children():
                self.users_tree.delete(item)
                
            if result["success"] and "users" in result["data"]:
                for user in result["data"]["users"]:
                    self.users_tree.insert('', tk.END, values=(
                        user.get('name', ''), 
                        user.get('email', ''),
                        'Yes' if user.get('admin') else 'No',
                        user.get('registered_on', '')
                    ))
                self.status_var.set(f"Fetched {len(result['data']['users'])} users")
            else:
                messagebox.showerror("Error", result.get("message", "Failed to fetch users"))
                self.status_var.set("Failed to fetch users")
        
        threading.Thread(target=fetch_thread).start()

def main():
    root = tk.Tk()
    app = LoginAPIGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
