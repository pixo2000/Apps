#!/usr/bin/env python3
"""
Icon generator for Recoder application
This script creates an .ico file that can be used as the executable icon
"""

from PIL import Image, ImageDraw
import os

def create_app_icon():
    """Create a simple app icon based on the progress bar design"""
    ICON_SIZE = 64
    
    # Create the icon image
    image = Image.new('RGBA', (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))  # Transparent background
    draw = ImageDraw.Draw(image)
    
    # Draw a rounded rectangle background
    margin = 4
    draw.rounded_rectangle([margin, margin, ICON_SIZE-margin-1, ICON_SIZE-margin-1], 
                          radius=8, fill='#2196F3', outline='#1976D2', width=2)
    
    # Draw a play symbol (triangle) in the center
    center_x, center_y = ICON_SIZE // 2, ICON_SIZE // 2
    triangle_size = 16
    
    # Triangle points (play button)
    points = [
        (center_x - triangle_size//2, center_y - triangle_size//2),
        (center_x - triangle_size//2, center_y + triangle_size//2),
        (center_x + triangle_size//2, center_y)
    ]
    draw.polygon(points, fill='white')
    
    # Add some text or symbol for video conversion
    text_y = center_y + triangle_size//2 + 4
    draw.text((center_x, text_y), "MP4", fill='white', anchor='mm', 
              font_size=10 if hasattr(draw, 'font_size') else None)
    
    return image

def create_icon_file():
    """Create the .ico file with multiple sizes"""
    # Create icons in different sizes (Windows expects multiple sizes in .ico files)
    sizes = [16, 24, 32, 48, 64, 128, 256]
    images = []
    
    for size in sizes:
        # Create icon for this size
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Draw background
        margin = max(1, size // 16)
        draw.rounded_rectangle([margin, margin, size-margin-1, size-margin-1], 
                              radius=max(2, size//8), fill='#2196F3', outline='#1976D2', width=max(1, size//32))
        
        # Draw play triangle
        center_x, center_y = size // 2, size // 2
        triangle_size = max(4, size // 4)
        
        points = [
            (center_x - triangle_size//2, center_y - triangle_size//2),
            (center_x - triangle_size//2, center_y + triangle_size//2),
            (center_x + triangle_size//2, center_y)
        ]
        draw.polygon(points, fill='white')
        
        # Add text for larger sizes
        if size >= 32:
            text_y = center_y + triangle_size//2 + max(1, size//16)
            font_size = max(6, size // 8)
            draw.text((center_x, text_y), "MP4", fill='white', anchor='mm')
        
        images.append(image)
    
    # Save as .ico file
    icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
    images[0].save(icon_path, format='ICO', sizes=[(img.width, img.height) for img in images])
    print(f"Icon created: {icon_path}")
    return icon_path

if __name__ == "__main__":
    create_icon_file()
    print("Icon file 'icon.ico' has been created!")
    print("You can now build your executable with the icon included.")
