import torch
from ultralytics import YOLO

torch.cuda.empty_cache()

model = YOLO("yolo26m.pt")

# Навчання
model.train(
    data="ai_module/dataset_2/data.yaml", 
    epochs=400,
    imgsz=640,
    batch=12,       
    workers=4,
    device="0",
    patience = 80,
    cache=True,
    amp=False,

    cos_lr=True,

    box=7.5,
    cls=1.5,
    
    degrees=10.0,
    translate=0.15,
    scale=0.3,
    shear=2.0,
    fliplr=0.5,
    
    hsv_h=0.02, 
    hsv_s=0.7,
    hsv_v=0.5,
    
    mosaic=1.0,
    mixup=0.2,
    copy_paste=0.15,
    erasing=0.2,
    close_mosaic=10,
    
    # Optimizer
    optimizer='AdamW',
    weight_decay=0.0005,
    lr0=0.0005,
    lrf=0.01,
    warmup_epochs=5.0,
)