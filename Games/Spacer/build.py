"""
Build script to compile the Spacer game into a single executable.
"""
import os
import subprocess
import shutil
from pathlib import Path
import sys
import tkinter as tk
from tkinter import filedialog

# Build configuration - easily change these values as needed
APP_NAME = "Spacer"
APP_VERSION = "1.0.0"  # Version number for the build
ICON_PATH = "icon.ico"  # Default path to the icon file
OUTPUT_NAME = f"{APP_NAME}-v{APP_VERSION}"  # Final executable name will include version
OUTPUT_DIR = "Spacer/release"  # Custom output directory instead of PyInstaller default

def check_tkinter():
    """Check if tkinter is installed, install if not, and restart the script"""
    try:
        import tkinter
        print("tkinter is already installed.")
        return True
    except ImportError:
        print("tkinter not found. Installing...")
        try:
            if os.name == "nt":  # Windows
                subprocess.check_call([sys.executable, "-m", "pip", "install", "tk"])
            else:  # Linux/macOS
                subprocess.check_call([sys.executable, "-m", "pip", "install", "python-tk"])
            print("tkinter installed successfully. Restarting script...")
            # Restart the current script
            os.execv(sys.executable, [sys.executable] + sys.argv)
            return True  # This line won't actually be reached due to restart
        except Exception as e:
            print(f"Failed to install tkinter: {e}")
            return False

def prompt_for_icon():
    """Open a file dialog to select an icon file"""
    try:
        # Create and hide the root Tkinter window
        root = tk.Tk()
        root.withdraw()
        
        # Show file dialog and get the selected file path
        file_path = filedialog.askopenfilename(
            title="Select Icon File",
            filetypes=[
                ("Icon Files", "*.ico"),
                ("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif;*.webp"),
                ("PNG Files", "*.png"),
                ("JPEG Files", "*.jpg;*.jpeg"),
                ("BMP Files", "*.bmp"),
                ("GIF Files", "*.gif"),
                ("WebP Files", "*.webp"),
                ("All Files", "*.*")
            ],
            initialdir=os.path.dirname(os.path.abspath(__file__))
        )
        
        # If user selected a file, return its path
        if (file_path):
            # If not an ICO file, convert it to ICO
            if not file_path.lower().endswith('.ico'):
                try:
                    # Make sure PIL/Pillow is installed
                    try:
                        from PIL import Image
                    except ImportError:
                        print("Pillow not found. Installing...")
                        subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
                        from PIL import Image
                    
                    # Open the image and convert to ICO
                    print(f"Converting {os.path.basename(file_path)} to ICO format...")
                    img = Image.open(file_path)
                    
                    # Resize if necessary (Windows icons are typically 256x256 or smaller)
                    max_size = 256
                    if max(img.size) > max_size:
                        print(f"Resizing image from {img.size} to fit within {max_size}x{max_size}...")
                        img.thumbnail((max_size, max_size), Image.LANCZOS)
                    
                    # If image has transparency and it's not a format that supports it
                    if img.mode == 'RGBA' and file_path.lower().endswith(('.jpg', '.jpeg', '.bmp')):
                        # Create a white background
                        background = Image.new('RGBA', img.size, (255, 255, 255, 255))
                        # Paste the image on the background
                        background.paste(img, (0, 0), img)
                        img = background.convert('RGB')
                    
                    # Save as ICO
                    ico_path = os.path.splitext(file_path)[0] + '.ico'
                    img.save(ico_path, format='ICO')
                    print(f"Converted to ICO: {ico_path}")
                    return ico_path
                except Exception as e:
                    print(f"Failed to convert to ICO: {e}")
                    print(f"Using original file {os.path.basename(file_path)} directly (may not work with all PyInstaller versions)")
                    return file_path
            return file_path
        
        return None
    except Exception as e:
        print(f"Error opening file dialog: {e}")
        print("Continuing without custom icon...")
        return None

def check_pyinstaller():
    """Check if PyInstaller is installed, install if not"""
    try:
        import PyInstaller
        print("PyInstaller is already installed.")
        return True
    except ImportError:
        print("PyInstaller not found. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("PyInstaller installed successfully.")
            return True
        except Exception as e:
            print(f"Failed to install PyInstaller: {e}")
            return False

def build_executable():
    """Build the Spacer game into a single executable"""
    print(f"\n=== Building {APP_NAME} v{APP_VERSION} Executable ===")
    
    # Check if PyInstaller is available
    if not check_pyinstaller():
        print("Cannot continue without PyInstaller.")
        return False
    
    # Create output directory if it doesn't exist
    Path(f"./{OUTPUT_DIR}").mkdir(exist_ok=True)
    
    # Prompt for icon file
    custom_icon = prompt_for_icon()
    
    # Use custom icon if selected, otherwise use default icon path
    icon_path = custom_icon if custom_icon else ICON_PATH
    
    # Define icon file path - create a placeholder comment if no icon exists
    icon_param = f"--icon={icon_path}" if os.path.exists(icon_path) else ""
    if not os.path.exists(icon_path):
        print(f"Warning: Icon file not found at {icon_path}")
        print("Building executable without icon.")
    else:
        print(f"Using icon: {icon_path}")
    
    # Get the absolute path to the main script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(script_dir, "main.py")
    
    # Verify main.py exists
    if not os.path.exists(main_script):
        print(f"\n✗ Error: main.py not found at {main_script}")
        print("Make sure you're running this script from the correct directory.")
        return False
    
    # Create data directories in dist folder to ensure they're available
    try:
        # Get path to dimensions folder
        dimensions_dir = os.path.join(script_dir, "dimensions")
        if not os.path.exists(dimensions_dir):
            print(f"Warning: dimensions directory not found at {dimensions_dir}")
            os.makedirs(dimensions_dir, exist_ok=True)
            print(f"Created empty dimensions directory at {dimensions_dir}")
        
        # Get current directory for module imports
        current_dir = os.path.abspath(os.getcwd())
        print(f"Working directory: {current_dir}")
        
        # Check for game_core module location
        game_core_paths = [
            os.path.join(current_dir, "game_core"),
            os.path.join(current_dir, "game_core.py"),
            os.path.join(script_dir, "game_core"),
            os.path.join(script_dir, "game_core.py")
        ]
        
        found_game_core = None
        for path in game_core_paths:
            if os.path.exists(path):
                found_game_core = path
                print(f"Found game_core at: {path}")
                break
        
        if not found_game_core:
            print("Warning: game_core module not found in expected locations.")
            print("Searching for game_core module...")
            
            # Try to find the module by walking the directory
            for root, dirs, files in os.walk(current_dir):
                if "game_core.py" in files or "game_core" in dirs:
                    found_game_core = os.path.join(root, "game_core.py" if "game_core.py" in files else "game_core")
                    print(f"Found game_core at: {found_game_core}")
                    break
        
        # Define PyInstaller command with absolute paths
        cmd = [
            "pyinstaller",
            "--onefile",  # Single executable
            "--name", OUTPUT_NAME,  # Name of the executable including version
            "--clean",  # Clean PyInstaller cache
            # Use console for debugging
            "--console",  # Show console for debugging
            "--distpath", OUTPUT_DIR,  # Set custom output directory
            "--workpath", f"{OUTPUT_DIR}/build",  # Set custom work directory
            "--specpath", f"{OUTPUT_DIR}/spec",  # Set custom spec directory
            "--hidden-import", "game_core",  # Add game_core as hidden import
            "--hidden-import", "dimensions",  # Include dimensions module
            "--path", current_dir,  # Add current directory to import paths
        ]
        
        # If we found the game_core module directory, add its parent as a path
        if found_game_core:
            module_parent = os.path.dirname(found_game_core)
            if module_parent and module_parent != current_dir:
                cmd.extend(["--path", module_parent])
        
        # Add data folder
        cmd.extend(["--add-data", f"{dimensions_dir}{os.pathsep}dimensions"])
        
        # Fix icon parameter for different platforms
        if os.path.exists(icon_path):
            print(f"Using icon: {icon_path}")
            if os.name == "nt":  # Windows
                cmd.extend(["--icon", icon_path])
            else:  # macOS/Linux
                cmd.extend(["--icon", icon_path])
        else:
            print(f"Warning: Icon file not found at {icon_path}")
            print("Building executable without icon.")
        
        # Add main script (with absolute path)
        cmd.append(main_script)
        
        # Execute PyInstaller
        print(f"Running command: {' '.join(cmd)}")
        subprocess.check_call(cmd)
        
        # Verify the executable was created
        exe_name = f"{OUTPUT_NAME}.exe" if os.name == "nt" else OUTPUT_NAME
        exe_path = os.path.join(OUTPUT_DIR, exe_name)
        
        if os.path.exists(exe_path):
            print(f"\n✓ Successfully built {exe_path}")
            
            # Create saves folder in output directory
            dist_saves = os.path.join(OUTPUT_DIR, "saves")
            os.makedirs(dist_saves, exist_ok=True)
            print(f"✓ Created {dist_saves} directory")
            
            # Create dimensions.json in output directory if needed
            dimensions_json = "dimensions.json"
            if os.path.exists(dimensions_json):
                shutil.copy(dimensions_json, os.path.join(OUTPUT_DIR, dimensions_json))
                print(f"✓ Copied {dimensions_json} to {OUTPUT_DIR} folder")
            
            print(f"\nBuild completed successfully for {APP_NAME} v{APP_VERSION}!")
            return True
        else:
            print(f"\n✗ Failed to find built executable at {exe_path}")
            return False
    
    except Exception as e:
        print(f"\n✗ Build failed with error: {e}")
        return False

if __name__ == "__main__":
    # Check if tkinter is available and install if needed
    if not check_tkinter():
        print("Warning: Failed to install tkinter - file dialog for icon selection will be skipped")
        # Continue with default icon or no icon
    
    build_executable()
