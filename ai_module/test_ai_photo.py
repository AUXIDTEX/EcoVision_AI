from ultralytics import YOLO
import glob
import os
import cv2


#model = YOLO("D:/Project Data/app/assets/Tree_disseses_finder.pt")
model = YOLO("/workspace/app/assets/Tree_disseses_finder.pt")


#input_path = "D:/Project Data/test_images/frame_101.jpg" # Шлях до картинки
input_path = "/workspace/test_images/frame_101.jpg" # Шлях до картинки

save_dir = "output_images"
os.makedirs(save_dir, exist_ok=True)


if not os.path.exists(input_path):
    print(f"Помилка: Файл {input_path} не знайдено.")
else:
    
    results = model(input_path, device='0')

    for i, r in enumerate(results):
        res_plotted = r.plot()

        
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        out_path = os.path.join(save_dir, f"{base_name}_result_{i}.jpg")

        
        cv2.imwrite(out_path, res_plotted)
        print(f"Зображення збережено: {out_path}")