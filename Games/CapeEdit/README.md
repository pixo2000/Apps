# GIF to Vertical Collage Converter

This Python program takes a GIF file as input, extracts all its frames, and creates a single PNG image where all frames are stacked vertically below each other.

## Requirements

- Python 3.6 or higher
- Pillow (PIL) library

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

Or install Pillow directly:
```bash
pip install Pillow
```

## Usage

### Command Line Usage

```bash
# Basic usage - output file will be auto-generated
python main.py path/to/your/animation.gif

# Specify custom output path
python main.py path/to/your/animation.gif path/to/output/collage.png
```

### Interactive Usage

Simply run the program without arguments and it will prompt you for input:

```bash
python main.py
```

## Features

- Extracts all frames from any GIF file
- Maintains original frame dimensions and quality
- Automatically handles different GIF formats and color modes
- Creates a vertical collage with all frames stacked below each other
- Saves the result as a PNG file with transparency support
- Auto-generates output filename if not specified
- Provides progress feedback during processing

## Example

If you have a GIF with 10 frames, each 100x100 pixels, the output PNG will be 100x1000 pixels with all frames arranged vertically.

## Error Handling

The program includes comprehensive error handling for:
- Missing input files
- Invalid GIF formats
- File permission issues
- Memory constraints for very large GIFs

## Output

The program will display:
- Number of frames extracted
- Progress while pasting frames
- Final output file path
- Any errors encountered during processing
