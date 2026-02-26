# EcoVision AI

EcoVision AI is a desktop application for detecting tree pathologies in images using computer vision.
<img width="2560" height="996" alt="Interface_ai" src="https://github.com/user-attachments/assets/ad582474-628f-4596-9769-bc05274a09ed" />

The project combines:
- visual image analysis in multiple modes;
- YOLO model inference for lesion detection;
- batch processing for photos and videos in future.

## System Capabilities

- Compare two images in point analysis mode.

  <img width="2560" height="1380" alt="Interface_points" src="https://github.com/user-attachments/assets/45ae9c36-f24e-43a7-957a-e2e9509b475e" />

- Analyze images with a grid and highlight deviation zones.

  <img width="2560" height="1380" alt="Interface_grid" src="https://github.com/user-attachments/assets/5ed2b40e-8081-4fec-ae96-22537bd1f98e" />

- Run AI detection for a single file or an entire folder.

  <img width="2560" height="1380" alt="Interface_ai2" src="https://github.com/user-attachments/assets/644f62c1-56eb-42de-afe8-f432facf4cee" />

- Apply spectral/color filters.

  <img width="2560" height="1380" alt="Interface_filterer" src="https://github.com/user-attachments/assets/0fb8f4aa-41c1-4acf-98f3-caa8f0631267" />


## Classes Detected by the Neural Network

The model detects 5 classes:

- `Tree Canker`
- `White Tree Patches`
- `Nectria Canker`
- `Transverse Canker`
- `Cankerous Deformation`

  <img width="200" height="910" alt="frame_89_result" src="https://github.com/user-attachments/assets/cee5cefb-40d5-42ab-bab9-0bb9c77dc591" />
  <img width="200" height="910" alt="frame_89_result (1)" src="https://github.com/user-attachments/assets/e962c61b-5fd0-4e28-8867-5b6476e240f0" />
  <img width="200" height="910" alt="frame_89_result (2)" src="https://github.com/user-attachments/assets/b8727afe-825e-40e2-b1f2-513052cb0091" />
  <img width="200" height="910" alt="frame_89_result (3)" src="https://github.com/user-attachments/assets/b1a562a8-00b1-4e21-b544-45bf2c8ca910" />


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

  <img width="2400" height="1200" alt="results" src="https://github.com/user-attachments/assets/d3a41bf2-a4ea-4de5-818c-161992ec8d6a" />


## Tech Stack

- Python
- PyQt6
- Ultralytics YOLO
- PyTorch
- NumPy
- Pillow

## Repository Structure

```text
app/
  main.py                     # GUI entry point
  logic/
    average_color.py          # average color calculation
    run_yolo.py               # YOLO inference + JSON output
  modules/
    ai_module.py              # ai processing code
    app_settings_manager.py   # settings manager
    category_widget.py        # widget for each image
    change_modes.py           # logic for changing analysis modes
    duped_layer.py            # overlay for points for 2nd image
    grid_analyzer.py          # grid-based analysis
    image_output.py           # average color output from area of the point
    json_mode_exporter.py     # function for exporting json reports
    main_window.py            # main window
    mode_exporter.py          # dialogue screen for settings manager
    pdf_mode_exporter.py      # function for exporting pdf reports
    point_placer.py           # overlay for points for 1st image
    second_column.py          # core logic
    selectable_imagebox.py    # logic for selecting images
    spectal_filterer.py       # image filtering
  assets/
    Tree_disseses_finder.pt   # model weights used by GUI
ai_module/
  train_AI.py
  train_ai_small_objects.py
test_dir/
  test_ai_photo.py            # test ai on image
  test_ai_folder.py           # test ai on folder of images
  test_AI_video.py            # test ai on video
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
