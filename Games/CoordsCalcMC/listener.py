import pyperclip
import time
from new_converter import convert_coords

def on_clipboard_change(new_content):
    print(f"New content: {new_content}")
    convert_coords(new_content)


def monitor_clipboard():
    last_content = pyperclip.paste()
    while True:
        time.sleep(0.5)  # Check every 0.5 seconds
        current_content = pyperclip.paste()
        if current_content != last_content:
            on_clipboard_change(current_content)
            last_content = current_content

if __name__ == '__main__':
    monitor_clipboard()