import socket
import threading
import ctypes
import time

HOST = '127.0.0.1'  # Change to server IP if needed
PORT = 65432

# Helper to set caps lock state (Windows only)
def set_caps_lock(state):
    VK_CAPITAL = 0x14
    hllDll = ctypes.WinDLL ("User32.dll")
    if bool(hllDll.GetKeyState(VK_CAPITAL)) != state:
        # Simulate key press
        ctypes.windll.user32.keybd_event(VK_CAPITAL, 0, 0, 0)
        ctypes.windll.user32.keybd_event(VK_CAPITAL, 0, 2, 0)

def get_caps_lock():
    VK_CAPITAL = 0x14
    return bool(ctypes.WinDLL("User32.dll").GetKeyState(VK_CAPITAL))

def listen_server(sock):
    while True:
        data = sock.recv(1024)
        if not data:
            break
        state = data.decode().strip() == 'True'
        set_caps_lock(state)
        print(f"[Server] CAPS_LOCK set to {state}")

def send_caps_lock(sock):
    last_state = get_caps_lock()
    while True:
        time.sleep(0.5)
        current_state = get_caps_lock()
        if current_state != last_state:
            sock.sendall(str(current_state).encode())
            last_state = current_state

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        threading.Thread(target=listen_server, args=(s,), daemon=True).start()
        send_caps_lock(s)

if __name__ == '__main__':
    main()
