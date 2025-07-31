# Stone App

A Python application for stone image processing and boundary extraction with real-time parameter adjustment.

## Features

### Step 1: Image Selection
- Image selection via drag-and-drop, file browser, or camera capture
- Support for multiple image formats (PNG, JPG, JPEG, GIF, BMP, WEBP)
- Live camera preview with capture, retake, and submit functionality
- Image preview and basic controls

### Step 2: Stone Segmentation (NEW!)
- **Automatic stone boundary detection** using computer vision techniques
- **Real-time parameter adjustment** with interactive sliders:
  - Blur Kernel Size (noise reduction)
  - Threshold Value (binary segmentation)
  - Erosion Iterations (noise removal)
  - Dilation Iterations (shape completion)
  - Minimum Contour Area (filter small objects)
- **Live preview** of segmentation results with boundary highlighting
- **Save/Load default parameters** for consistent processing
- **Navigation controls** to return to image selection or proceed to next step

## Requirements

- Python 3.7+
- CustomTkinter 5.2.2
- PIL (Pillow) 11.3.0
- OpenCV 4.12.0.88
- NumPy 2.2.6
- tkinterdnd2 0.4.3

## Installation

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python stone_gui.py`

## Usage

### Basic Workflow
1. **Launch the application**: `python stone_gui.py`
2. **Select an image** using one of three methods:
   - Drag and drop an image file onto the drop zone
   - Click "Browse" to select from file system
   - Click "Camera" to capture a new image
3. **Start processing**: Click "Start Processing" to open the segmentation window
4. **Adjust parameters**: Use the sliders to fine-tune stone boundary detection
5. **Save settings**: Click "Set as Default" to save current parameters
6. **Navigate**: Use "Delete Image" to return to step 1 or "Start" for next step

### Segmentation Parameters
- **Blur Kernel Size**: Controls noise reduction (1-15, odd numbers)
- **Threshold Value**: Binary segmentation threshold (0-255)
- **Erosion Iterations**: Removes noise and small artifacts (0-10)
- **Dilation Iterations**: Fills gaps and completes shapes (0-10)
- **Min Contour Area**: Filters out small objects (100-10000 pixels)

## File Structure

```
stone/
├── stone_gui.py              # Main application window
├── cameraCapture.py          # Camera capture functionality
├── segmentation_window.py    # Stone segmentation interface
├── requirements.txt          # Python dependencies
├── instructions.txt          # Project specifications
├── drop_image.png           # UI icon for drag-and-drop
├── test_segmentation.py     # Testing utilities
└── README.md               # This file
```

## Testing

Run the test script to verify segmentation functionality:
```bash
python test_segmentation.py
```

This creates a test image and verifies that the segmentation algorithm can detect stone boundaries.
