import time
import pyperclip

# small bug: when starting, you need to copy something before it works ingame


def split_string(string, number, symbol):
    parts = string.split(symbol)
    if len(parts) > number:
        return parts[number]
    else:
        return None


def convert_coords(x, y, z, dimension):
    x = float(x)
    y = float(y)
    z = float(z)
    if dimension == "overworld":
        x_temp = x / 8
        z_temp = z / 8
        y_temp = y
        x = split_string(str(x_temp), 0, ".")
        y = split_string(str(y_temp), 0, ".")
        z = split_string(str(z_temp), 0, ".")
        print(f"New Coords: {x}, {y}, {z}")
    elif dimension == "nether":
        x_temp = x * 8
        z_temp = z * 8
        y_temp = y
        x = split_string(str(x_temp), 0, ".")
        y = split_string(str(y_temp), 0, ".")
        z = split_string(str(z_temp), 0, ".")
        print(f"New Coords: {x}, {y}, {z}")
    else:
        print("No dimension found")


def extract_coords(string):  # negative coords?
    x_temp = split_string(string, 6, " ")
    y_temp = split_string(string, 7, " ")
    z_temp = split_string(string, 8, " ")
    x = split_string(x_temp, 0, ".")
    y = split_string(y_temp, 0, ".")
    z = split_string(z_temp, 0, ".")
    print(f"Coords: {x}, {y}, {z}")
    return x, y, z


def extract_dimension(string):
    dimension_temp = split_string(string, 2, " ")
    dimension = split_string(dimension_temp, 1, ":")
    print(f"Dimension: {dimension}")
    return dimension


def on_clipboard_change(new_content):
    print(f"New content: {new_content}")
    if new_content.startswith("/execute in minecraft:overworld run tp @s"):  # only world with nether
        x, y, z = extract_coords(new_content)
        dimension = extract_dimension(new_content)
        convert_coords(x, y, z, dimension)


def monitor_clipboard(callback):
    last_content = pyperclip.paste()
    while True:
        time.sleep(0.5)  # Check every 0.5 seconds
        current_content = pyperclip.paste()
        if current_content != last_content:
            callback(current_content)
            last_content = current_content


if __name__ == '__main__':
    monitor_clipboard(on_clipboard_change())
