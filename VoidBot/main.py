# add looking down

# import other stuff
import pyautogui
import time
import keyboard
import sys
import pyperclip

# definitions
def copy_to_clipboard(text):
    pyperclip.copy(text)
    print(f"Copied to clipboard: '{text}'")

def switch_to_minecraft():
    print("Switching to Minecraft...")
    pyautogui.keyDown('alt')
    pyautogui.press('tab')
    pyautogui.keyUp('alt')
    time.sleep(1)  # Wait for window to focus
    print("Switched to Minecraft!")

def load_hotbar():
    print("Loading hotbar with . and 4...")
    pyautogui.keyDown('.')
    pyautogui.keyDown('4')
    time.sleep(0.1)
    pyautogui.keyUp('4')
    pyautogui.keyUp('.')
    time.sleep(0.5)
    
    print("Selecting slot 1...")
    pyautogui.press('1')
    time.sleep(0.5)

def send_message(text):
    # Press T to open chat
    pyautogui.press('t')
    time.sleep(0.2)
    
    # Type the message
    pyautogui.keyDown('ctrl')
    pyautogui.press('v')
    pyautogui.keyUp('ctrl')
    time.sleep(0.2)
    
    # Press Enter to send
    pyautogui.press('enter')

def select_slot(slot_number):
    """Select a specific slot in the hotbar"""
    pyautogui.press(str(slot_number))
    print(f"Selected slot {slot_number}")
    time.sleep(0.2)

# globals
WAIT_TIME = 19  # Seconds between actions
MESSAGE_TEXT = "#goto ~ ~ ~1"  # The text to type
EXIT_KEY = 'esc'  # Key to press to stop the bot

# main loop
def main():
    # Copy message to clipboard at start
    copy_to_clipboard(MESSAGE_TEXT)
    
    print(f"Waiting 5 seconds before starting...")
    print(f"Press '{EXIT_KEY}' at any time to stop the bot")
    time.sleep(5)  # Wait for 5 seconds
    
    switch_to_minecraft()
    load_hotbar()
    
    print("Starting auto-click and message loop...")
    print(f"The bot will send: '{MESSAGE_TEXT}'")
    print(f"Press '{EXIT_KEY}' to exit")
    
    # Track which slot we're using
    current_slot = 1
    
    try:
        while not keyboard.is_pressed(EXIT_KEY):
            # Select the current slot
            select_slot(current_slot)
            
            # Right click
            pyautogui.leftClick()
            time.sleep(0.5)
            
            # Send message
            send_message(MESSAGE_TEXT)
            
            # Alternate between slots 1 and 2
            current_slot = 2 if current_slot == 1 else 1
            
            # Wait before next cycle
            print(f"Waiting {WAIT_TIME} seconds...")
            
            # Check for exit key during wait
            wait_start = time.time()
            while time.time() - wait_start < WAIT_TIME:
                if keyboard.is_pressed(EXIT_KEY):
                    break
                time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("Bot stopped by user (Ctrl+C)")
    
    print("Bot stopped")

if __name__ == "__main__":
    main()