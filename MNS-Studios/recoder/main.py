import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import threading
import pystray
from PIL import Image, ImageDraw
import re
import keyboard

# Tray icon image
ICON_SIZE = 64

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
    tray_icon.title = "FFmpeg Progress"
    try:
        proc = subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True)
        for line in proc.stderr:
            if duration is None:
                m = duration_pattern.search(line)
                if m:
                    h, m_, s = map(float, m.groups())
                    duration = h*3600 + m_*60 + s
            m = time_pattern.search(line)
            if m and duration:
                h, m_, s = map(float, m.groups())
                current = h*3600 + m_*60 + s
                percent = min(100, int(current/duration*100))
                tray_icon.icon = show_progress_bar(percent)
                remaining = max(0, duration-current)
                mins, secs = divmod(int(remaining), 60)
                hours, mins = divmod(mins, 60)
                tray_icon.title = f"Remaining: {hours:02}:{mins:02}:{secs:02}"
        proc.wait()
    finally:
        tray_icon.icon = show_progress_bar(100)
        tray_icon.title = "Done!"
    # Show finished popup
    def show_finished_popup(output_path):
        popup = tk.Tk()
        popup.withdraw()
        result = messagebox.askquestion(
            "Conversion finished",
            f"Done! Output saved to:\n{output_path}\n\nOpen folder?",
            icon='info',
            type='yesno',
            parent=popup
        )
        popup.destroy()
        if result == 'yes':
            # Open parent folder and select file
            subprocess.run(f'explorer /select,"{output_path}"')
    threading.Thread(target=show_finished_popup, args=(output_path,), daemon=True).start()

def select_and_convert(tray_icon):
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)  # Always on top
    input_path = filedialog.askopenfilename(title="Select MOV file", filetypes=[("MOV files", "*.mov")], parent=root)
    if input_path:
        base, _ = os.path.splitext(input_path)
        output_path = base + ".mp4"
        if os.path.exists(output_path):
            overwrite = messagebox.askyesno("Overwrite?", f"File '{output_path}' already exists. Overwrite?", parent=root)
            if not overwrite:
                print("Conversion cancelled.")
                return
        ffmpeg_cmd = [
            r"D:\ffmpeg\bin\ffmpeg.exe",
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

def on_hotkey(tray_icon):
    select_and_convert(tray_icon)

def on_exit(icon, item):
    icon.stop()
    os._exit(0)

def tray_app():
    icon = pystray.Icon("recoder", show_progress_bar(0), "Recoder", menu=pystray.Menu(
        pystray.MenuItem("Exit", on_exit)
    ))
    def hotkey_listener():
        keyboard.add_hotkey('ctrl+alt+x', lambda: on_hotkey(icon))
        keyboard.wait()
    threading.Thread(target=hotkey_listener, daemon=True).start()
    icon.run()

if __name__ == "__main__":
    tray_app()