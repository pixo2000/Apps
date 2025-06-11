from pynput import keyboard
from pynput.keyboard import Key, KeyCode
import sys
import time
import threading
import tkinter as tk
from tkinter import ttk

class SnapTapGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SnapTap Controller")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        self.snap_tap = None
        self.is_running = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="SnapTap", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Status
        self.status_label = ttk.Label(main_frame, text="Status: Stopped", font=("Arial", 10))
        self.status_label.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        # Key state display frame
        key_frame = ttk.LabelFrame(main_frame, text="Key States", padding="10")
        key_frame.grid(row=2, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))
        
        # Physical keys display
        ttk.Label(key_frame, text="Physical Keys:").grid(row=0, column=0, sticky=tk.W)
        self.physical_keys_label = ttk.Label(key_frame, text="None", font=("Courier", 10))
        self.physical_keys_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # Active keys display
        ttk.Label(key_frame, text="Active Keys:").grid(row=1, column=0, sticky=tk.W)
        self.active_keys_label = ttk.Label(key_frame, text="None", font=("Courier", 10))
        self.active_keys_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        # Last active display
        ttk.Label(key_frame, text="Last Active:").grid(row=2, column=0, sticky=tk.W)
        self.last_active_label = ttk.Label(key_frame, text="None", font=("Courier", 10))
        self.last_active_label.grid(row=2, column=1, sticky=tk.W, padx=(10, 0))
        
        # Control buttons
        self.start_button = ttk.Button(main_frame, text="Start SnapTap", command=self.start_snaptap)
        self.start_button.grid(row=3, column=0, padx=(0, 5), pady=5, sticky=tk.W+tk.E)
        
        self.stop_button = ttk.Button(main_frame, text="Stop SnapTap", command=self.stop_snaptap, state=tk.DISABLED)
        self.stop_button.grid(row=3, column=1, padx=(5, 0), pady=5, sticky=tk.W+tk.E)
        
        # Info text
        info_text = tk.Text(main_frame, height=8, width=60, wrap=tk.WORD)
        info_text.grid(row=4, column=0, columnspan=2, pady=(10, 0), sticky=(tk.W, tk.E))
        
        info_content = """SnapTap Features:

• Automatic key conflict resolution for WASD movement
• A/D keys cancel each other out
• W/S keys cancel each other out
• Sticky key functionality - previously held keys resume when conflicting keys are released

Note: Uses pynput for cross-platform compatibility without admin privileges."""
        
        info_text.insert(tk.END, info_content)
        info_text.config(state=tk.DISABLED)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        key_frame.columnconfigure(1, weight=1)
        
    def update_key_display(self, physical_keys, active_keys, last_active):
        """Update the key state display"""
        def format_keys(keys):
            if not keys:
                return "None"
            return ", ".join([k.char if hasattr(k, 'char') else str(k) for k in keys])
        
        def format_last_active(last_active):
            if not last_active:
                return "None"
            result = []
            for group, key in last_active.items():
                key_char = key.char if hasattr(key, 'char') else str(key)
                result.append(f"{group}: {key_char}")
            return ", ".join(result)
        
        self.physical_keys_label.config(text=format_keys(physical_keys))
        self.active_keys_label.config(text=format_keys(active_keys))
        self.last_active_label.config(text=format_last_active(last_active))
        
    def start_snaptap(self):
        if not self.is_running:
            self.snap_tap = SnapTap(self.update_status, self.update_key_display)
            self.snap_tap.start()
            
    def stop_snaptap(self):
        if self.is_running and self.snap_tap:
            self.snap_tap.stop()
            
    def update_status(self, status):
        self.status_label.config(text=f"Status: {status}")
        if "Running" in status:
            self.is_running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
        else:
            self.is_running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        
    def on_closing(self):
        if self.is_running:
            self.stop_snaptap()
        self.root.destroy()

class SnapTap:
    def __init__(self, status_callback=None, key_display_callback=None):
        # Define key groups that conflict with each other
        self.key_groups = {
            'horizontal': {KeyCode.from_char('a'), KeyCode.from_char('d')},
            'vertical': {KeyCode.from_char('w'), KeyCode.from_char('s')}
        }
        
        # Track which keys are currently held down by the user (physically pressed)
        self.physical_keys = set()
        
        # Track which keys we've artificially released (need to be restored)
        self.suppressed_keys = set()
        
        # Track the last active key in each group for sticky functionality
        self.last_active = {}
        
        self.listener = None
        self.controller = keyboard.Controller()
        self.running = False
        self.status_callback = status_callback
        self.key_display_callback = key_display_callback
        
    def get_key_group(self, key):
        """Return the group name for a given key"""
        for group_name, keys in self.key_groups.items():
            if key in keys:
                return group_name
        return None
    
    def update_display(self):
        """Update the GUI display with current key states"""
        if self.key_display_callback:
            # Active keys are physical keys minus suppressed keys
            active_keys = self.physical_keys - self.suppressed_keys
            self.key_display_callback(
                self.physical_keys.copy(),
                active_keys,
                self.last_active.copy()
            )
    
    def on_key_press(self, key):
        """Handle key press events"""
        try:
            group = self.get_key_group(key)
            if not group:
                return  # Not a movement key, let it pass through
                
            # Mark as physically pressed
            self.physical_keys.add(key)
            
            # Remove from suppressed if it was there
            self.suppressed_keys.discard(key)
            
            # Check if any conflicting keys in the same group are active
            conflicting_keys = self.key_groups[group] - {key}
            active_conflicting = conflicting_keys.intersection(self.physical_keys - self.suppressed_keys)
            
            if active_conflicting:
                # Suppress all conflicting active keys
                for conflicting_key in active_conflicting:
                    try:
                        self.controller.release(conflicting_key)
                        self.suppressed_keys.add(conflicting_key)
                    except:
                        pass  # Ignore release errors
            
            # Update last active for this group
            self.last_active[group] = key
            
            self.update_display()
            
        except Exception as e:
            print(f"Error in key press handler: {e}")
    
    def on_key_release(self, key):
        """Handle key release events"""
        try:
            group = self.get_key_group(key)
            if not group:
                return  # Not a movement key, let it pass through
                
            # Mark as physically released
            self.physical_keys.discard(key)
            self.suppressed_keys.discard(key)
            
            # Sticky functionality: Check if we need to restore another key in this group
            if group in self.last_active and self.last_active[group] == key:
                # Look for other keys in this group that are still physically held but suppressed
                other_keys = self.key_groups[group] - {key}
                for other_key in other_keys:
                    if other_key in self.physical_keys and other_key in self.suppressed_keys:
                        # Restore the other key by removing it from suppressed and pressing it
                        try:
                            self.controller.press(other_key)
                            self.suppressed_keys.discard(other_key)
                            self.last_active[group] = other_key
                            break
                        except:
                            pass  # Ignore press errors
            
            self.update_display()
                            
        except Exception as e:
            print(f"Error in key release handler: {e}")
    
    def start(self):
        """Start SnapTap"""
        try:
            if self.status_callback:
                self.status_callback("Starting...")
            
            self.running = True
            
            # Start the keyboard listener without suppression
            self.listener = keyboard.Listener(
                on_press=self.on_key_press,
                on_release=self.on_key_release,
                suppress=False
            )
            self.listener.start()
            
            if self.status_callback:
                self.status_callback("Running")
                
        except Exception as e:
            error_msg = str(e)
            if self.status_callback:
                self.status_callback(f"Error: {error_msg}")
            raise e
    
    def stop(self):
        """Stop SnapTap"""
        self.running = False
        if self.listener:
            self.listener.stop()
            self.listener = None
        
        # Restore any suppressed keys before clearing
        for key in list(self.suppressed_keys):
            if key in self.physical_keys:
                try:
                    self.controller.press(key)
                except:
                    pass
        
        # Clear all tracking
        self.physical_keys.clear()
        self.suppressed_keys.clear()
        self.last_active.clear()
        
        if self.status_callback:
            self.status_callback("Stopped")
        
        if self.key_display_callback:
            self.key_display_callback(set(), set(), {})

if __name__ == "__main__":
    print("SnapTap - No administrator privileges required!")
    print("Make sure you have pynput installed: pip install pynput")
    
    gui = SnapTapGUI()
    gui.run()
