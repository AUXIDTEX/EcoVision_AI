# EcoVision AI

EcoVision AI is a desktop application for detecting tree pathologies in images using computer vision.

The project combines:
- visual image analysis in multiple modes;
- YOLO model inference for lesion detection;
- batch processing for photos and videos.

## System Capabilities

- Compare two images in point analysis mode.
- Analyze images with a grid and highlight deviation zones.
- Run AI detection for a single file or an entire folder.
- Apply spectral/color filters.

## Classes Detected by the Neural Network

The model detects 5 classes:

- `Tree Canker`
- `White Tree Patches`
- `Nectria Canker`
- `Transverse Canker`
- `Cankerous Deformation`

## Current Model Metrics

Based on the validation results:

- `mAP@0.5 (all classes)`: **0.738**
- `F1 max (all classes)`: **0.72** at `confidence=0.356`

AP@0.5 by class:

- `Cankerous Deformation`: **0.544**
- `Nectria Canker`: **0.562**
- `Transverse Canker`: **0.995**
- `Tree Canker`: **0.928**
- `White Tree Patches`: **0.663**

Additional:

- `Precision peak (all classes)`: **1.00** at `confidence=0.955`
- `Recall at confidence=0.0 (all classes)`: **0.91**

## Tech Stack

- Python
- PyQt6
- Ultralytics YOLO
- PyTorch
- NumPy / Pillow

## Repository Structure

```text
app/
  main.py                     # GUI entry point
  logic/
    run_yolo.py               # YOLO inference + JSON output
    average_color.py          # average color calculation
  modules/
    main_window.py            # main window
    second_column.py          # core mode logic
    grid_analyzer.py          # grid-based analysis
    spectal_filterer.py       # image filtering
  assets/
    Tree_disseses_finder.pt   # model weights used by GUI
ai_module/
  train_AI.py
  train_ai_small_objects.py
  test_ai_photo.py
  test_ai_folder.py
  test_AI_video.py
requirements.txt
```

## Quick Start

### 1. Install dependencies

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Run the application

```powershell
py -3 app/main.py
```

## CLI Inference (Single Image)

```powershell
py -3 app/logic/run_yolo.py "path\to\image.jpg"
```

The script returns JSON to `stdout`:
- `inference/preprocess/postprocess speed`
- `output_path`
- `detections[]` (`class_name`, `conf`, `xyxy`)

## Video and Folder Processing

For tests and batch processing, use:

- `ai_module/test_ai_photo.py`
- `ai_module/test_ai_folder.py`
- `ai_module/test_AI_video.py`

## Model Training

Training scripts:

- `ai_module/train_ai_small_objects.py -- Recommended` 
- `ai_module/train_AI.py`

Typical project parameters:

- `epochs=400`
- `imgsz=640`
- `optimizer='AdamW'`

## Note

`requirements.txt` includes a broad package set. For minimal GUI startup, the critical packages are: `PyQt6`, `ultralytics`, `torch`, `numpy`, `Pillow`.
