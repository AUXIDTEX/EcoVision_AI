import torch
from ultralytics import YOLO

torch.cuda.empty_cache()

model = YOLO("models/yolo12n.pt")

# Навчання
model.train(
    data="ai_module/dataset/data.yaml", 
    epochs=400,
    imgsz=640,
    batch=24,       
    workers=4,
    device="0",
    patience = 40,

    #cos_lr=True,

    box=7.5,
    cls=1.5,
    
    degrees=10.0,
    translate=0.15,
    scale=0.3,
    shear=2.0,
    fliplr=0.5,
    
    hsv_h=0.02,  # не треба багато - у тебе вже різні кольори!
    hsv_s=0.7,
    hsv_v=0.5,
    
    mosaic=1.0,
    mixup=0.0,
    copy_paste=0.15,
    erasing=0.2,
    
    # Optimizer
    optimizer='AdamW',
    weight_decay=0.0005,
    lr0=0.001,
    lrf=0.01,
    warmup_epochs=5.0,
)