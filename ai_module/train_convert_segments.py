import os
import yaml
import shutil
from pathlib import Path
import numpy as np
from tqdm import tqdm
from ultralytics.utils.ops import segments2boxes
from ultralytics import YOLO
import torch

def process_labels_to_clean_dir(original_labels_dir, suffix="_temp_boxes"):
    """Конвертує сегменти в бокси і повертає шлях до нової тимчасової папки."""
    original_labels_dir = Path(original_labels_dir).absolute()
    if not original_labels_dir.exists():
        return None
        
    clean_dir = original_labels_dir.parent / (original_labels_dir.name + suffix)
    clean_dir.mkdir(parents=True, exist_ok=True)
    
    label_files = list(original_labels_dir.glob("*.txt"))
    if not label_files:
        return str(clean_dir)

    print(f"--- Конвертація: {original_labels_dir} ({len(label_files)} файлів) ---")
    for label_path in tqdm(label_files):
        with open(label_path, 'r') as f:
            lines = f.readlines()

        new_labels = []
        for line in lines:
            parts = line.split()
            if len(parts) > 5: # Якщо точок > 4 (+1 для class_id)
                class_id = parts[0]
                seg = np.array(parts[1:], dtype=np.float32).reshape(-1, 2)
                box = segments2boxes([seg])[0] # Повертає [x, y, w, h]
                new_labels.append(f"{int(class_id)} {' '.join(map(str, box))}\n")
            else:
                new_labels.append(line)

        with open(clean_dir / label_path.name, 'w') as f:
            f.writelines(new_labels)
    return str(clean_dir)

# --- НАЛАШТУВАННЯ ШЛЯХІВ ---
project_root = Path("/workspace").absolute()
dataset_root = project_root / "ai_module/dataset_2"
original_yaml_path = dataset_root / "data.yaml"

with open(original_yaml_path, 'r') as f:
    data_cfg = yaml.safe_load(f)

# Визначаємо шляхи за вашою структурою: dataset/train/labels
label_dirs = {
    'train': dataset_root / "train/labels",
    'val': dataset_root / "val/labels"
}

# 1. Створюємо чисті лейбли (з'являться папки train/labels_temp_boxes)
tmp_labels = {
    'train': process_labels_to_clean_dir(label_dirs['train']),
    'val': process_labels_to_clean_dir(label_dirs['val'])
}

# 2. Створюємо тимчасовий запускний майданчик
tmp_run_dir = dataset_root / "tmp_run"
if tmp_run_dir.exists(): shutil.rmtree(tmp_run_dir)
tmp_run_dir.mkdir(parents=True)

data_cfg_temp = data_cfg.copy()
data_cfg_temp['path'] = str(project_root) # Базовий шлях для YOLO



for split in ['train', 'val']:
    split_dir = tmp_run_dir / split
    (split_dir / "images").mkdir(parents=True)
    
    # Лінкуємо картинки (вони в dataset/train/images або dataset/train)
    # Беремо шлях з YAML
    orig_img_dir = (dataset_root / data_cfg[split]).absolute()
    for img in orig_img_dir.glob("*"):
        if img.is_file() and img.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
            os.symlink(img, split_dir / "images" / img.name)
    
    # Лінкуємо наші чисті лейбли в tmp_run/split/labels
    os.symlink(Path(tmp_labels[split]).absolute(), split_dir / "labels")
    
    # Оновлюємо шлях у YAML на нову тимчасову папку images
    data_cfg_temp[split] = str((split_dir / "images").absolute())

tmp_yaml_path = dataset_root / "temp_data_boxes.yaml"
with open(tmp_yaml_path, 'w') as f:
    yaml.dump(data_cfg_temp, f)

# --- НАВЧАННЯ ---
try:
    torch.cuda.empty_cache()

    print(f"BF16 supported: {torch.cuda.is_bf16_supported()}")

    model = YOLO("yolo26m.pt")
    #model = YOLO("/workspace/runs/detect/train_auto/train_fixed_amp/weights/best.pt")

    model.to("cuda")

    # Навчання
    model.train(
        data=tmp_yaml_path, 
        epochs=5,
        imgsz=640,
        batch=16,       
        workers=2,
        device="0",
        patience = 80,
        #cache=True,
        
        amp=True,
        half=False,   

        save=True,
        save_period=10,
        project="/workspace/runs/detect/train_auto",

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
        optimizer='SGD',
        weight_decay=0.0005,
        lr0=0.01,
        lrf=0.01,
        warmup_epochs=5.0,
    )

finally:
    print("Очищення тимчасових даних...")
    if tmp_run_dir.exists(): shutil.rmtree(tmp_run_dir)
    for p in tmp_labels.values():
        if p and Path(p).exists(): shutil.rmtree(p)
    if tmp_yaml_path.exists(): os.remove(tmp_yaml_path)