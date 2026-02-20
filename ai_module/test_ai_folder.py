from ultralytics import YOLO
import os
import cv2
import glob
import torch

# 1. Завантаження моделі
model = YOLO("/workspace/app/assets/Tree_disseses_finder.pt")

torch.cuda.empty_cache()  # Очищуємо кеш GPU перед початком

print("Розігрів GPU...")
dummy_input = torch.zeros(1, 3, 640, 640).to('cuda') # Створюємо порожній тензор
model(dummy_input, verbose=False) # Проганяємо його через модель
print("GPU готовий до роботи.")



# 2. Налаштування шляхів
input_dir = "/workspace/ai_module/Frames/packet2/small/train/"  # Папка з вхідними фото
save_dir = "output_images"
os.makedirs(save_dir, exist_ok=True)

# Шукаємо всі файли з розширеннями зображень
image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.JPG']
image_files = []
for ext in image_extensions:
    image_files.extend(glob.glob(os.path.join(input_dir, ext)))

if not image_files:
    print(f"У папці {input_dir} не знайдено зображень.")
else:
    print(f"Знайдено зображень: {len(image_files)}. Починаю обробку...")

    # 3. Запуск детекції (передаємо весь список файлів відразу)
    # stream=True допомагає економити пам'ять, якщо фоток дуже багато
    results = model(image_files, device='0', stream=True)

    for i, r in enumerate(results):
        # Отримуємо оригінальний шлях до файлу, щоб зберегти назву
        original_filename = os.path.basename(r.path)
        base_name = os.path.splitext(original_filename)[0]
        
        # Малюємо бокси
        res_plotted = r.plot()

        # Формуємо шлях збереження
        out_path = os.path.join(save_dir, f"{base_name}_result.jpg")

        # Зберігаємо
        cv2.imwrite(out_path, res_plotted)
        
        # Виводимо прогрес
        print(f"[{i+1}/{len(image_files)}] Оброблено: {original_filename} -> {out_path}")

print("\nВсі зображення успішно оброблені!")