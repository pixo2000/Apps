import socket
import threading
import tkinter as tk
from tkinter import filedialog, simpledialog
import keyboard
import os
import sys
import pyperclip
import io  # Added import for io
import pystray
from PIL import Image, ImageDraw
import ctypes
import time

# --- CONFIG ---
FILE_HOTKEY = 'ctrl+alt+f'  # Hotkey to send selected file
CLIPBOARD_HOTKEY = 'ctrl+alt+c'  # Hotkey to send clipboard
PORT = 5000
BUFFER_SIZE = 4096

# --- GUI for IP input ---
def get_ip_and_mode():
    root = tk.Tk()
    root.withdraw()
    ip = simpledialog.askstring('Connect', 'Enter IP of other PC (leave blank to host):')
    root.destroy()
    if ip:
        return ip, 'client'
    else:
        return '', 'server'

def get_peer_ip():
    import socket
    local_ip = socket.gethostbyname(socket.gethostname())
    # fallback: get correct IP if multiple interfaces
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        pass
    if local_ip == '10.68.242.153':
        return '10.68.242.106'
    elif local_ip == '10.68.242.106':
        return '10.68.242.153'
    else:
        print(f'Unknown local IP: {local_ip}. Exiting.')
        sys.exit(1)

sync_enabled = True

def send_disable_sync(ip):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, PORT))
        s.send(b'DISSYNC ')
        s.close()
        print('Sent disable sync command to peer.')
    except Exception as e:
        print(f'Disable sync error: {e}')

# --- Server ---
def handle_connection(conn, addr, peer_ip):
    if addr[0] != peer_ip:
        print(f"Rejected connection from {addr[0]}")
        conn.close()
        return
    try:
        while True:
            header = conn.recv(8)
            if not header:
                break
            mode = header.decode().strip()
            if mode == 'FILE':
                filename_len = int.from_bytes(conn.recv(2), 'big')
                filename = conn.recv(filename_len).decode()
                filesize = int.from_bytes(conn.recv(8), 'big')
                print(f"Receiving file: {filename} ({filesize} bytes)")
                with open(filename, 'wb') as f:
                    received = 0
                    while received < filesize:
                        data = conn.recv(min(BUFFER_SIZE, filesize - received))
                        if not data:
                            break
                        f.write(data)
                        received += len(data)
                print(f'Received file: {filename}')
            elif mode == 'CLIP':
                cliptype = conn.recv(4).decode()
                if cliptype == 'TEXT':
                    textlen = int.from_bytes(conn.recv(4), 'big')
                    text = conn.recv(textlen).decode()
                    pyperclip.copy(text)
                    print('Received clipboard text.')
                elif cliptype == 'IMG_':
                    imgsize = int.from_bytes(conn.recv(8), 'big')
                    imgdata = b''
                    while len(imgdata) < imgsize:
                        chunk = conn.recv(min(BUFFER_SIZE, imgsize - len(imgdata)))
                        if not chunk:
                            break
                        imgdata += chunk
                    tmpfile = 'received_clipboard.png'
                    with open(tmpfile, 'wb') as f:
                        f.write(imgdata)
                    try:
                        import win32clipboard
                        from PIL import Image
                        img = Image.open(tmpfile)
                        output = io.BytesIO()
                        img.convert('RGB').save(output, 'BMP')
                        data = output.getvalue()[14:]
                        win32clipboard.OpenClipboard()
                        win32clipboard.EmptyClipboard()
                        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
                        win32clipboard.CloseClipboard()
                        print('Received clipboard image.')
                    except Exception as e:
                        print('Image clipboard failed:', e)
            elif mode == 'CAPSLOCK':
                state = conn.recv(1)
                VK_CAPITAL = 0x14
                # Set caps lock state
                caps_state = ctypes.windll.user32.GetKeyState(VK_CAPITAL) & 1
                if state == b'1' and not caps_state:
                    ctypes.windll.user32.keybd_event(VK_CAPITAL, 0, 0, 0)
                elif state == b'0' and caps_state:
                    ctypes.windll.user32.keybd_event(VK_CAPITAL, 0, 0, 0)
                print(f"Caps Lock set to: {'ON' if state == b'1' else 'OFF'}")
            elif mode == 'DISSYNC':
                global sync_enabled
                sync_enabled = False
                print('Caps Lock sync disabled by peer.')
    except Exception as e:
        print(f'Server error: {e}')
    finally:
        conn.close()

def server_thread():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', PORT))
    s.listen(5)
    print(f'Server listening on port {PORT}...')
    peer_ip = get_peer_ip()
    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_connection, args=(conn, addr, peer_ip), daemon=True).start()
    s.close()

# --- Client ---
def send_file(ip, filepath):
    filesize = os.path.getsize(filepath)
    if filesize > 100 * 1024 * 1024:  # 100MB limit
        print("File too large!")
        return
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, PORT))
    s.send(b'FILE    ')
    filename = os.path.basename(filepath)
    s.send(len(filename).to_bytes(2, 'big'))
    s.send(filename.encode())
    s.send(filesize.to_bytes(8, 'big'))
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(BUFFER_SIZE)
            if not data:
                break
            s.send(data)
    s.close()
    print(f'Sent file: {filename}')

def send_clipboard(ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, PORT))
    try:
        from PIL import ImageGrab
        img = ImageGrab.grabclipboard()
        if img:
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            imgdata = buf.getvalue()
            s.send(b'CLIP    ')
            s.send(b'IMG_')
            s.send(len(imgdata).to_bytes(8, 'big'))
            s.send(imgdata)
            print('Sent clipboard image.')
            s.close()
            return
    except Exception:
        pass
    text = pyperclip.paste()
    if isinstance(text, str) and text:
        s.send(b'CLIP    ')
        s.send(b'TEXT')
        s.send(len(text.encode()).to_bytes(4, 'big'))
        s.send(text.encode())
        print('Sent clipboard text.')
    s.close()

def send_capslock(ip, state):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, PORT))
        s.send(b'CAPSLOCK')
        s.send(b'1' if state else b'0')
        s.close()
        print(f"Sent Caps Lock state: {'ON' if state else 'OFF'}")
    except Exception as e:
        print(f"Caps Lock sync error: {e}")

# --- Hotkey Handlers ---
def file_hotkey(ip):
    print('[File Hotkey] Triggered!')
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        filepath = filedialog.askopenfilename(title='Select file to send')
        root.destroy()
        if filepath:
            print(f'[File Hotkey] Selected file: {filepath}')
            threading.Thread(target=send_file, args=(ip, filepath), daemon=True).start()
        else:
            print('[File Hotkey] No file selected.')
    except Exception as e:
        print(f'[File Hotkey] Error: {e}')

def clipboard_hotkey(ip):
    threading.Thread(target=send_clipboard, args=(ip,), daemon=True).start()

# --- Caps Lock Sync ---
def capslock_listener(ip):
    global sync_enabled
    def on_capslock(e):
        if sync_enabled:
            state = keyboard.is_pressed('caps lock')
            for _ in range(3):
                try:
                    send_capslock(ip, state)
                    break
                except Exception:
                    time.sleep(1)
    def on_ctrl_capslock(e):
        global sync_enabled
        sync_enabled = not sync_enabled
        print(f'Caps Lock sync enabled: {sync_enabled}')
        if not sync_enabled:
            send_disable_sync(ip)
    keyboard.on_press_key('caps lock', on_capslock)
    keyboard.add_hotkey('ctrl+caps lock', on_ctrl_capslock)
    while True:
        time.sleep(1)  # Keep thread alive

# --- System Tray ---
def create_tray_icon():
    # Create a simple icon
    icon_img = Image.new('RGB', (64, 64), color='blue')
    d = ImageDraw.Draw(icon_img)
    d.rectangle([16, 16, 48, 48], fill='white')
    icon = pystray.Icon('fileswitch', icon_img, 'FileSwitch')
    icon.menu = pystray.Menu(
        pystray.MenuItem('Exit', lambda: sys.exit(0))
    )
    threading.Thread(target=icon.run, daemon=True).start()

# --- Main ---
if __name__ == '__main__':
    peer_ip = get_peer_ip()
    print(f'Local IP detected. Will connect to peer: {peer_ip}')
    threading.Thread(target=server_thread, daemon=True).start()
    print(f'Hotkeys: {FILE_HOTKEY} (file), {CLIPBOARD_HOTKEY} (clipboard)')
    keyboard.add_hotkey(FILE_HOTKEY, lambda: file_hotkey(peer_ip))
    keyboard.add_hotkey(CLIPBOARD_HOTKEY, lambda: clipboard_hotkey(peer_ip))
    threading.Thread(target=capslock_listener, args=(peer_ip,), daemon=True).start()
    print('Running in system tray. Use tray icon to exit.')
    create_tray_icon()
    while True:
        keyboard.wait('esc')  # Still allow ESC to exit if tray fails