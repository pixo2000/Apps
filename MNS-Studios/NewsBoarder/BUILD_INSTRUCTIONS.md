# NewsBoarder - Build Instructions

## Quick Build

### Option 1: Using PowerShell (Recommended)
```powershell
.\build.ps1
```

### Option 2: Using Batch File
```cmd
build.bat
```

### Option 3: Manual Build
```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create the icon
python create_icon.py

# 3. Build the executable
pyinstaller NewsBoarder.spec --clean
```

## Output

The compiled executable will be located in the `dist` folder:
- `dist\NewsBoarder.exe`

## Requirements

- Python 3.8 or higher
- pip (Python package manager)

## Dependencies

The following packages will be installed automatically:
- customtkinter >= 5.2.0
- requests >= 2.31.0
- pyinstaller >= 6.0.0
- pillow >= 10.0.0
- cairosvg >= 2.7.0

## Icon

The application uses a custom Carrd icon that is automatically converted from SVG to ICO format during the build process.

## Troubleshooting

### Build fails with "icon.ico not found"
Run `python create_icon.py` manually to create the icon file.

### Missing dependencies
Run `pip install -r requirements.txt` to install all required packages.

### CairoSVG installation issues on Windows
CairoSVG requires GTK+ runtime. If you encounter issues:
1. Download and install GTK+ from https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer
2. Or use the alternative icon creation method below

### Alternative Icon Creation (if CairoSVG fails)
If you have issues with CairoSVG, you can manually create the icon:
1. Open `icon.svg` in a browser or image editor
2. Save/export it as PNG (256x256 or larger)
3. Use an online converter or tool to convert PNG to ICO
4. Save as `icon.ico` in the project directory

## Distribution

The executable in the `dist` folder is standalone and can be distributed without Python installed on the target system. Make sure to include the `template.setting` file in the same directory as the executable.
