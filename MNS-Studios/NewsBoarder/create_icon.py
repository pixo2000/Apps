"""
Simple SVG to ICO converter using Pillow
Creates a basic icon from the SVG path data
"""
from PIL import Image, ImageDraw
import os

def create_icon_from_svg():
    """Creates an icon with the Carrd logo design"""
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    
    images = []
    for size in sizes:
        # Create a new image with white background
        img = Image.new('RGB', size, color='white')
        draw = ImageDraw.Draw(img)
        
        # Scale factor for the design
        scale = size[0] / 24.0
        
        # Draw a simplified version of the Carrd logo
        # Using basic shapes since we can't render SVG paths directly
        
        # Background - keep white
        
        # Draw main shapes (simplified representation)
        # Left triangular area
        left_points = [
            (int(3 * scale), int(1 * scale)),
            (int(3 * scale), int(15 * scale)),
            (int(9 * scale), int(12 * scale)),
            (int(9 * scale), int(4 * scale))
        ]
        draw.polygon(left_points, fill='#0066FF')
        
        # Right area
        right_points = [
            (int(10 * scale), int(4 * scale)),
            (int(10 * scale), int(23 * scale)),
            (int(20.5 * scale), int(18 * scale)),
            (int(20.5 * scale), int(4 * scale))
        ]
        draw.polygon(right_points, fill='#0052CC')
        
        # Add some detail lines
        for i in range(3):
            y_pos = int((12 + i * 3.3) * scale)
            draw.line(
                [(int(12 * scale), y_pos), (int(18 * scale), y_pos)],
                fill='white',
                width=max(1, int(scale * 0.5))
            )
        
        images.append(img)
    
    # Save as ICO with multiple sizes
    ico_path = 'icon.ico'
    images[0].save(
        ico_path, 
        format='ICO', 
        sizes=[img.size for img in images],
        append_images=images[1:]
    )
    
    print(f"✓ Icon created successfully: {ico_path}")
    print(f"  Created {len(sizes)} sizes: {', '.join(f'{s[0]}x{s[1]}' for s in sizes)}")
    return ico_path

if __name__ == "__main__":
    print("Creating icon from SVG design...")
    print("-" * 50)
    
    try:
        icon_path = create_icon_from_svg()
        
        # Verify the file was created
        if os.path.exists(icon_path):
            file_size = os.path.getsize(icon_path)
            print(f"  File size: {file_size:,} bytes")
            print("-" * 50)
            print("SUCCESS! Icon is ready for PyInstaller.")
        else:
            print("ERROR: Icon file was not created!")
            exit(1)
            
    except Exception as e:
        print(f"ERROR: {e}")
        print("\nTip: Make sure Pillow is installed:")
        print("  pip install pillow")
        exit(1)
