import os
import shutil

# Шляхи
images_folder = "ai_module/dataset/images/val"
labels_folder = "ai_module/dataset/labels/val"
bad_folder = "bad folder"

os.makedirs(bad_folder, exist_ok=True)

# Отримуємо всі імена лейблів без розширення
label_files = {os.path.splitext(f)[0] for f in os.listdir(labels_folder) if f.endswith(".txt")}

# Перевіряємо всі зображення
for img_file in os.listdir(images_folder):
    if not img_file.lower().endswith(".jpg"):
        continue

    img_name = os.path.splitext(img_file)[0]

    if img_name not in label_files:
        # Переміщаємо кадр у bad
        shutil.move(os.path.join(images_folder, img_file), os.path.join(bad_folder, img_file))

        # Якщо випадково є лейбл, теж перемістимо (для безпеки)
        label_path = os.path.join(labels_folder, img_name + ".txt")
        if os.path.exists(label_path):
            shutil.move(label_path, os.path.join(bad_folder, img_name + ".txt"))

        print(f"[!] Переміщено поганий кадр: {img_file}")

print("✅ Готово!")
