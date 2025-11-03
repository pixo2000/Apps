import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import threading
import pystray
from PIL import Image, ImageDraw
import re
import keyboard
import pyperclip
import sys

# Tray icon image
ICON_SIZE = 64

def get_ffmpeg_path():
    """Get the correct path to FFmpeg executable, whether running as script or exe"""
    if getattr(sys, 'frozen', False):
        # Running as bundled executable
        bundle_dir = sys._MEIPASS
        ffmpeg_path = os.path.join(bundle_dir, 'ffmpeg', 'ffmpeg.exe')
    else:
        # Running as script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        ffmpeg_path = os.path.join(script_dir, 'ffmpeg', 'ffmpeg.exe')
    return ffmpeg_path

def show_progress_bar(percent):
    image = Image.new('RGB', (ICON_SIZE, ICON_SIZE), 'white')
    draw = ImageDraw.Draw(image)
    draw.rectangle([0, 0, ICON_SIZE-1, ICON_SIZE-1], outline='black')
    bar_width = int((ICON_SIZE-4) * percent / 100)
    draw.rectangle([2, ICON_SIZE//2-8, 2+bar_width, ICON_SIZE//2+8], fill='blue')
    return image

def run_ffmpeg_with_progress(cmd, output_path, tray_icon):
    duration = None
    duration_pattern = re.compile(r"Duration: (\d+):(\d+):(\d+\.\d+)")
    time_pattern = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")
    tray_icon.icon = show_progress_bar(0)
    tray_icon.title = "Starting conversion..."
    try:
        proc = subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True, text=True)
        for line in proc.stderr:
            print(f"FFmpeg output: {line.strip()}")  # Debug output
            if duration is None:
                m = duration_pattern.search(line)
                if m:
                    h, m_min, s = map(float, m.groups())
                    duration = h*3600 + m_min*60 + s
                    print(f"Total duration: {duration} seconds")
            
            if duration is not None:
                m = time_pattern.search(line)
                if m:
                    h, m_min, s = map(float, m.groups())
                    current = h*3600 + m_min*60 + s
                    percent = min(100, int((current/duration)*100))
                    tray_icon.icon = show_progress_bar(percent)
                    remaining = max(0, duration-current)
                    mins, secs = divmod(int(remaining), 60)
                    hours, mins = divmod(mins, 60)
                    tray_icon.title = f"Progress: {percent}% - Remaining: {hours:02}:{mins:02}:{secs:02}"
        proc.wait()
        if proc.returncode != 0:
            tray_icon.title = "Conversion failed!"
        else:
            tray_icon.title = "Conversion complete!"
    except Exception as e:
        print(f"Error during conversion: {e}")
        tray_icon.title = "Error occurred!"
    finally:
        tray_icon.icon = show_progress_bar(100)
    # Show finished popup and copy folder path to clipboard
    def show_finished_popup(output_path):
        folder_path = os.path.dirname(output_path)
        pyperclip.copy(folder_path)
        popup = tk.Tk()
        popup.withdraw()
        messagebox.showinfo(
            "Conversion finished",
            f"Done! Output saved to:\n{output_path}\n\nFolder path copied to clipboard!",
            parent=popup
        )
        popup.destroy()
    threading.Thread(target=show_finished_popup, args=(output_path,), daemon=True).start()

def select_and_convert(tray_icon):
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)  # Always on top
    try:
        input_path = filedialog.askopenfilename(title="Select MOV file", filetypes=[("MOV files", "*.mov")], parent=root)
        if input_path:
            base, _ = os.path.splitext(input_path)
            output_path = base + ".mp4"
            if os.path.exists(output_path):
                overwrite = messagebox.askyesno("Overwrite?", f"File '{output_path}' already exists. Overwrite?", parent=root)
                if not overwrite:
                    print("Conversion cancelled.")
                    return
            # Get FFmpeg path (works for both script and exe)
            ffmpeg_path = get_ffmpeg_path()
            
            # Check if ffmpeg exists
            if not os.path.exists(ffmpeg_path):
                messagebox.showerror("Error", f"FFmpeg not found at: {ffmpeg_path}", parent=root)
                return
            
            print(f"Using ffmpeg at: {ffmpeg_path}")
            ffmpeg_cmd = [
                ffmpeg_path,
                "-i", input_path,
                "-c:v", "libx264",
                "-preset", "slow",
                "-crf", "18",
                "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                "-b:a", "256k",
                "-ar", "48000",
                output_path
            ]
            threading.Thread(target=run_ffmpeg_with_progress, args=(ffmpeg_cmd, output_path, tray_icon), daemon=True).start()
        else:
            print("No file selected.")
    finally:
        root.destroy()

def on_hotkey(tray_icon):
    select_and_convert(tray_icon)

def on_convert_click(icon, item):
    select_and_convert(icon)

def on_exit(icon, item):
    icon.stop()
    os._exit(0)

def tray_app():
    icon = pystray.Icon("recoder", show_progress_bar(0), "Recoder", menu=pystray.Menu(
        pystray.MenuItem("Convert MOV to MP4", on_convert_click),
        pystray.MenuItem("Exit", on_exit)
    ))
    def hotkey_listener():
        keyboard.add_hotkey('ctrl+alt+x', lambda: on_hotkey(icon))
        keyboard.wait()
    threading.Thread(target=hotkey_listener, daemon=True).start()
    icon.run()

if __name__ == "__main__":
    tray_app()