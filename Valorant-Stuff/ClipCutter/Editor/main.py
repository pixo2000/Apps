import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
import os
import time

def select_video_file():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(
        title="Select MP4 video file",
        filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
    )
    return file_path if file_path else None

def calculate_circle_parameters(width, height, reference_width=1280, reference_height=780):
    # Original parameters for 1280x780 resolution
    ref_center_x, ref_center_y = 165, 200
    ref_diameter = 330
    
    # Calculate scale factors
    scale_x = width / reference_width
    scale_y = height / reference_height
    
    # Apply scale to get new parameters
    center_x = int(ref_center_x * scale_x)
    center_y = int(ref_center_y * scale_y)
    radius = int((ref_diameter / 2) * min(scale_x, scale_y))  # Use minimum scale to ensure circle fits
    
    return center_x, center_y, radius

def process_video(input_path):
    try:
        # Get output path
        filename = os.path.basename(input_path)
        name, ext = os.path.splitext(filename)
        output_path = os.path.join(os.path.dirname(input_path), f"{name}_circle{ext}")
        
        # Open the video
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            print(f"Error: Could not open video file {input_path}")
            return None
        
        # Get video properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Calculate circle parameters based on video resolution
        center_x, center_y, radius = calculate_circle_parameters(width, height)
        print(f"Video resolution: {width}x{height}")
        print(f"Circle parameters: center=({center_x}, {center_y}), radius={radius}")
        
        # Define crop size (diameter of the circle)
        crop_size = radius * 2
        
        # Create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (crop_size, crop_size))
        
        # Create a circular mask
        mask = np.zeros((crop_size, crop_size), dtype=np.uint8)
        cv2.circle(mask, (crop_size//2, crop_size//2), radius, 255, -1)
        
        # Process each frame
        frame_idx = 0
        start_time = time.time()
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Calculate crop coordinates
            x1 = max(0, center_x - radius)
            y1 = max(0, center_y - radius)
            x2 = min(width, center_x + radius)
            y2 = min(height, center_y + radius)
            
            # Create a black result frame
            result = np.zeros((crop_size, crop_size, 3), dtype=np.uint8)
            
            # Extract the region of interest
            roi_width = x2 - x1
            roi_height = y2 - y1
            
            if roi_width > 0 and roi_height > 0:
                # Position in the result frame where the ROI should be placed
                pos_x = 0 if x1 == 0 else crop_size - roi_width if x2 == width else (crop_size - roi_width) // 2
                pos_y = 0 if y1 == 0 else crop_size - roi_height if y2 == height else (crop_size - roi_height) // 2
                
                # Extract ROI from the original frame
                roi = frame[y1:y2, x1:x2]
                
                # Place ROI in the result frame
                result[pos_y:pos_y+roi_height, pos_x:pos_x+roi_width] = roi
            
            # Apply the circular mask
            mask_3channel = cv2.merge([mask, mask, mask])
            masked_result = cv2.bitwise_and(result, mask_3channel)
            
            # Write the frame
            out.write(masked_result)
            
            # Print progress
            frame_idx += 1
            if frame_idx % 30 == 0 or frame_idx == frame_count:
                elapsed_time = time.time() - start_time
                fps_processing = frame_idx / elapsed_time if elapsed_time > 0 else 0
                eta = (frame_count - frame_idx) / fps_processing if fps_processing > 0 else 0
                print(f"Processed {frame_idx}/{frame_count} frames ({frame_idx/frame_count*100:.1f}%) - "
                      f"Speed: {fps_processing:.1f} fps, ETA: {eta:.1f} seconds")
        
        # Release resources
        cap.release()
        out.release()
        
        print(f"Processing complete. Output saved to {output_path}")
        return output_path
        
    except Exception as e:
        print(f"Error processing video: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("Select an MP4 video file to crop to a circle")
    input_path = select_video_file()
    if not input_path:
        print("No file selected. Exiting.")
        return
    
    output_path = process_video(input_path)
    
    if output_path:
        print(f"Video processing completed successfully!")
        # Optionally open the output folder
        os.startfile(os.path.dirname(output_path))
    else:
        print("Video processing failed.")

if __name__ == "__main__":
    main()
