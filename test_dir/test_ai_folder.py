from ultralytics import YOLO
import os
import cv2
import glob
import torch


model = YOLO("/workspace/app/assets/Tree_disseses_finder.pt")

torch.cuda.empty_cache() 

print("Розігрів GPU...")
dummy_input = torch.zeros(1, 3, 640, 640).to('cuda') 
model(dummy_input, verbose=False) 
print("GPU готовий до роботи.")


# 2. Налаштування шляхів
input_dir = "/workspace/ai_module/Frames/packet2/small/train/"  # Папка з вхідними фото
save_dir = "output_images"
os.makedirs(save_dir, exist_ok=True)


image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.JPG']
image_files = []
for ext in image_extensions:
    image_files.extend(glob.glob(os.path.join(input_dir, ext)))

if not image_files:
    print(f"У папці {input_dir} не знайдено зображень.")
else:
    print(f"Знайдено зображень: {len(image_files)}. Починаю обробку...")

    
    results = model(image_files, device='0', stream=True)

    for i, r in enumerate(results):
        
        original_filename = os.path.basename(r.path)
        base_name = os.path.splitext(original_filename)[0]
        
        
        res_plotted = r.plot()

        
        out_path = os.path.join(save_dir, f"{base_name}_result.jpg")

        
        cv2.imwrite(out_path, res_plotted)
        
       
        print(f"[{i+1}/{len(image_files)}] Оброблено: {original_filename} -> {out_path}")

print("\nВсі зображення успішно оброблені!")