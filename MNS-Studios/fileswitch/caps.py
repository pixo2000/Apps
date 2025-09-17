import ctypes
import time

VK_CAPITAL = 0x14

def set_capslock(state: bool):
    caps_state = ctypes.WinDLL("User32.dll").GetKeyState(VK_CAPITAL)
    if (caps_state & 1) != state:
        ctypes.WinDLL("User32.dll").keybd_event(VK_CAPITAL, 0, 0, 0)
        ctypes.WinDLL("User32.dll").keybd_event(VK_CAPITAL, 0, 2, 0)

if __name__ == "__main__":
    print("Enabling Caps Lock...")
    set_capslock(True)
    time.sleep(2)
    print("Disabling Caps Lock...")
    set_capslock(False)
