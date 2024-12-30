import time
import pyperclip

def split_string(string, number):
    parts = string.split()
    if len(parts) > number:
        return parts[number]
    else:
        return None

def split_coords(string):
    parts = string.split(".")
    if len(parts) > 0:
        return parts[0]
    else:
        return None

def split_dimension(string):
    parts = string.split(":")
    if len(parts) > 1:
        return parts[1]
    else:
        return None

def convert_coords(x, y, z, dimension):
    if dimension == "overworld":
        x = x * 8
        z = z * 8
        print(f"{x}, {y}, {z}")
    elif dimension == "nether":
        x = x / 8
        z = z / 8
        print(f"{x}, {y}, {z}")

def get_last_element_from_clipboard():
    clipboard_content = pyperclip.paste()
    elements = clipboard_content.split()
    if elements:
        return elements[-1]
    else:
        return None

def copy(command):
    if command.startswith("/execute in minecraft:overworld run tp @s"):
        x1 = split_string(command, 6)
        y1 = split_string(command, 7)
        z1 = split_string(command, 8)
        x = split_coords(x1)
        y = split_coords(y1)
        z = split_coords(z1)
        return x, y, z
    else:
        return None

def on_clipboard_change(new_content):
    dimensiontemp = split_string(new_content, 3)
    dimension = split_dimension(dimensiontemp)
    coords = copy(new_content)
    if coords:
        x, y, z = coords
        x = int(x)
        y = int(y)
        z = int(z)
        convert_coords(x, y, z, dimension)

def monitor_clipboard(callback):
    previous_content = None
    while True:
        current_content = pyperclip.paste()
        if current_content != previous_content:
            previous_content = current_content
            callback(current_content)
        time.sleep(1)

# Start monitoring the clipboard
monitor_clipboard(on_clipboard_change)


