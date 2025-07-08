# Face Detect / Blur

A simple Python application that uses a graphical interface to detect or blur faces in images, videos, or live webcam feeds. Processed files are saved to an output directory next to the script.

---

## Features

- Choose between two regimes:
  - Detect: draw bounding boxes around faces
  - Blur: apply a blur effect to face regions
- Process static images (JPG, PNG), video files (MP4, AVI, MOV), or real-time webcam feed
- Automatic creation of an `output` folder for saving results
- Progress and error messages via the GUI

---

## Requirements

- Python 3.7 or newer
- Tkinter (usually included with standard Python installations)
- OpenCV  
- MediaPipe  

---

## Installation

1. Clone the repository:  
   ```bash
   git clone https://github.com/yourusername/face-detect-blur.git
   cd face-detect-blur
