import os
import sys
import argparse
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
import time
import shutil
import re

def get_video_dimensions(video_path):
    """Get the dimensions of a video using ffprobe."""
    cmd = [
        'ffprobe', 
        '-v', 'error', 
        '-select_streams', 'v:0', 
        '-show_entries', 'stream=width,height', 
        '-of', 'csv=p=0', 
        str(video_path)
    ]
    output = subprocess.check_output(cmd).decode('utf-8').strip().split(',')
    width, height = map(int, output)
    return width, height

def calculate_crop_params(width, height):
    """Calculate crop parameters to achieve 16:9 aspect ratio from the center."""
    target_ratio = 16 / 9
    current_ratio = width / height
    
    if abs(current_ratio - target_ratio) < 0.01:  # Already close to 16:9
        return 0, 0, width, height
    
    if current_ratio > target_ratio:  # Too wide (e.g., 21:9), crop width
        new_width = int(height * target_ratio)
        crop_left = (width - new_width) // 2
        return crop_left, 0, new_width, height
    else:  # Too tall, crop height
        new_height = int(width / target_ratio)
        crop_top = (height - new_height) // 2
        return 0, crop_top, width, new_height

def get_video_duration(video_path):
    """Get the duration of a video in seconds using ffprobe."""
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'csv=p=0',
        str(video_path)
    ]
    output = subprocess.check_output(cmd).decode('utf-8').strip()
    return float(output)

def crop_video(input_path, output_path, crop_left, crop_top, crop_width, crop_height):
    """Crop a video using ffmpeg with a real progress bar."""
    # Get video duration for progress calculation
    try:
        duration = get_video_duration(input_path)
        print(f"Video duration: {duration:.2f} seconds")
    except Exception as e:
        print(f"Warning: Couldn't get video duration: {e}")
        duration = 0
    
    cmd = [
        'ffmpeg',
        '-i', str(input_path),
        '-filter:v', f'crop={crop_width}:{crop_height}:{crop_left}:{crop_top}',
        '-c:a', 'copy',
        str(output_path),
        '-y'  # Overwrite output files without asking
    ]
    
    # Start process with pipe to get output
    process = subprocess.Popen(
        cmd, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        universal_newlines=True,
        bufsize=1
    )
    
    # Get terminal width for progress bar
    term_width = shutil.get_terminal_size().columns - 20
    
    # Progress pattern from ffmpeg output
    time_pattern = re.compile(r'time=(\d+):(\d+):(\d+\.\d+)')
    
    try:
        # Initialize progress tracking
        last_progress = 0
        
        # While process is running
        while process.poll() is None:
            # Read a line from stderr
            line = process.stderr.readline()
            
            # Look for time information
            if 'time=' in line:
                match = time_pattern.search(line)
                if match and duration > 0:
                    h, m, s = map(float, match.groups())
                    current_time = h * 3600 + m * 60 + s
                    percent = min(int((current_time / duration) * 100), 100)
                    
                    # Only update if progress has changed
                    if percent > last_progress:
                        last_progress = percent
                        progress = "█" * int(percent * term_width / 100)
                        remaining = " " * (term_width - int(percent * term_width / 100))
                        sys.stdout.write(f"\rProgress: |{progress}{remaining}| {percent}% ")
                        sys.stdout.flush()
        
        # Complete the progress bar at 100%
        progress = "█" * term_width
        sys.stdout.write(f"\rProgress: |{progress}| 100% ")
        sys.stdout.write("\n")  # New line after progress
        
        if process.returncode == 0:
            print(f"Successfully cropped: {output_path}")
            return True
        else:
            print(f"Error cropping video: ffmpeg exited with code {process.returncode}")
            return False
            
    except Exception as e:
        print(f"Error during video processing: {e}")
        # Make sure to terminate the process if an exception occurs
        process.terminate()
        return False

def open_file_explorer(path):
    """Open the specified path in File Explorer."""
    path = Path(path)
    if path.is_file():
        path = path.parent
    os.startfile(str(path))

def process_video(video_path):
    """Process a single video file to crop it to 16:9."""
    video_path = Path(video_path)
    if not video_path.is_file() or video_path.suffix.lower() != '.mp4':
        print(f"Skipping {video_path} - not an MP4 file")
        return None
    
    try:
        # Get video dimensions
        width, height = get_video_dimensions(video_path)
        print(f"Original dimensions: {width}x{height}")
        
        # Calculate crop parameters
        crop_left, crop_top, crop_width, crop_height = calculate_crop_params(width, height)
        print(f"Crop parameters: x={crop_left}, y={crop_top}, width={crop_width}, height={crop_height}")
        
        # Prepare output filename
        output_path = video_path.with_name(f"{video_path.stem}_cropped{video_path.suffix}")
        
        # Crop the video
        crop_success = crop_video(video_path, output_path, crop_left, crop_top, crop_width, crop_height)
        return output_path if crop_success else None
    
    except Exception as e:
        print(f"Error processing {video_path}: {str(e)}")
        return None

def main():
    # Create a hidden root window for the file dialog
    root = tk.Tk()
    root.withdraw()
    
    # Show file dialog to select a file or directory
    file_path = filedialog.askopenfilename(
        title="Select an MP4 file",
        filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
    )
    
    if not file_path:
        # Try directory selection if file selection was cancelled
        dir_path = filedialog.askdirectory(title="Or select a folder with MP4 files")
        if not dir_path:
            print("No input selected. Exiting.")
            return
        input_path = Path(dir_path)
    else:
        input_path = Path(file_path)
    
    last_output_path = None
    
    if input_path.is_file():
        # Process a single file
        print(f"Processing file: {input_path.name}")
        last_output_path = process_video(input_path)
    elif input_path.is_dir():
        # Process all MP4 files in the directory
        mp4_files = list(input_path.glob('*.mp4'))
        total_files = len(mp4_files)
        
        if total_files == 0:
            print("No MP4 files found in the selected directory.")
            return
        
        print(f"Found {total_files} MP4 files to process")
        
        # Get terminal width for progress bar
        term_width = shutil.get_terminal_size().columns - 30
        
        for idx, file_path in enumerate(mp4_files, 1):
            # Display overall progress
            percent = int((idx-1) / total_files * 100)
            progress = "█" * int(percent * term_width / 100)
            remaining = " " * (term_width - int(percent * term_width / 100))
            print(f"\nOverall progress: |{progress}{remaining}| {percent}% ({idx-1}/{total_files})")
            
            print(f"Processing file {idx}/{total_files}: {file_path.name}")
            output_path = process_video(file_path)
            if output_path:
                last_output_path = output_path
                
        # Show 100% completion
        progress = "█" * term_width
        print(f"\nOverall progress: |{progress}| 100% ({total_files}/{total_files})")
    else:
        print(f"Error: {input_path} is neither a file nor a directory")
        return
    
    # Open the output location in File Explorer
    if last_output_path:
        open_file_explorer(last_output_path)

if __name__ == "__main__":
    main()
