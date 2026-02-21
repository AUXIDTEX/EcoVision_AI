import torch
from ultralytics import YOLO

torch.cuda.empty_cache()

model = YOLO("yolov8n.pt")

# Навчання
model.train(
    data="ai_module/dataset/data.yaml", 
    epochs=400,
    imgsz=640,
    batch=24,       
    workers=4,
    device="cuda",
    patience = 20,
    augment = True,
    
    
    optimizer='AdamW',
)