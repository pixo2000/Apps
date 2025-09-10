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

# --- Server ---
def server_thread():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', PORT))
    s.listen(1)
    print(f'Server listening on port {PORT}...')
    conn, addr = s.accept()
    print(f'Connected by {addr}')
    while True:
        header = conn.recv(8)
        if not header:
            break
        mode = header.decode().strip()
        if mode == 'FILE':
            filename_len = int.from_bytes(conn.recv(2), 'big')
            filename = conn.recv(filename_len).decode()
            filesize = int.from_bytes(conn.recv(8), 'big')
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
                    imgdata += conn.recv(min(BUFFER_SIZE, imgsize - len(imgdata)))
                # Save image to temp and copy to clipboard
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
    s.close()

# --- Client ---
def send_file(ip, filepath):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, PORT))
    s.send(b'FILE    ')
    filename = os.path.basename(filepath)
    s.send(len(filename).to_bytes(2, 'big'))
    s.send(filename.encode())
    filesize = os.path.getsize(filepath)
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
    # Try image first
    try:
        import win32clipboard
        from PIL import ImageGrab
        img = ImageGrab.grabclipboard()
        if img:
            import io
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
    # Fallback to text
    text = pyperclip.paste()
    if isinstance(text, str) and text:
        s.send(b'CLIP    ')
        s.send(b'TEXT')
        s.send(len(text.encode()).to_bytes(4, 'big'))
        s.send(text.encode())
        print('Sent clipboard text.')
    s.close()

# --- Hotkey Handlers ---
def file_hotkey(ip):
    root = tk.Tk()
    root.withdraw()
    filepath = filedialog.askopenfilename(title='Select file to send')
    root.destroy()
    if filepath:
        send_file(ip, filepath)

def clipboard_hotkey(ip):
    send_clipboard(ip)

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
    # Ask for peer IP (other PC)
    root = tk.Tk()
    root.withdraw()
    peer_ip = simpledialog.askstring('Connect', 'Enter IP of other PC:')
    root.destroy()
    if not peer_ip:
        print('No peer IP entered. Exiting.')
        sys.exit(0)
    # Start server in background
    threading.Thread(target=server_thread, daemon=True).start()
    # Register hotkeys for sending to peer
    print(f'Hotkeys: {FILE_HOTKEY} (file), {CLIPBOARD_HOTKEY} (clipboard)')
    keyboard.add_hotkey(FILE_HOTKEY, lambda: file_hotkey(peer_ip))
    keyboard.add_hotkey(CLIPBOARD_HOTKEY, lambda: clipboard_hotkey(peer_ip))
    print('Running in system tray. Use tray icon to exit.')
    create_tray_icon()
    while True:
        keyboard.wait('esc')  # Still allow ESC to exit if tray fails