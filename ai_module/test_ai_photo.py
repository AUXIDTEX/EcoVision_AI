from ultralytics import YOLO
import glob
import os
import cv2

# Завантаження моделі
#model = YOLO("D:/Project Data/app/assets/Tree_disseses_finder.pt")
model = YOLO("/workspace/app/assets/Tree_disseses_finder.pt")

# Налаштування шляхів
#input_path = "D:/Project Data/test_images/640px.jpg" # Шлях до картинки
input_path = "/workspace/test_images/frame_39.jpg" # Шлях до картинки

save_dir = "output_images"
os.makedirs(save_dir, exist_ok=True)

# Перевіряємо, чи існує файл
if not os.path.exists(input_path):
    print(f"Помилка: Файл {input_path} не знайдено.")
else:
    # Запуск детекції
    # stream=False для поодиноких зображень зазвичай зручніше
    results = model(input_path, device='0')

    for i, r in enumerate(results):
        # Отримуємо зображення з намальованими боксами (у форматі BGR для OpenCV)
        res_plotted = r.plot()

        # Формуємо назву файлу
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        out_path = os.path.join(save_dir, f"{base_name}_result_{i}.jpg")

        # Зберігаємо на диск
        cv2.imwrite(out_path, res_plotted)
        print(f"Зображення збережено: {out_path}")