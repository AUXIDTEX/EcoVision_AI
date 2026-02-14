import os
import random
import shutil

# Налаштування
source_dir = "/media/auxidtex/Local Disk/Project Data/ai_module/Frames/packet2/big/train"      # папка з зображеннями
target_dir = "/media/auxidtex/Local Disk/Project Data/ai_module/Frames/packet2/big/test"    # куди переміщати
count = 40                        # скільки зображень перемістити

# Створити папку призначення, якщо нема
os.makedirs(target_dir, exist_ok=True)

# Розширення зображень
extensions = ('.jpg', '.jpeg', '.png', '.webp', '.bmp')

# Список зображень
images = [f for f in os.listdir(source_dir) if f.lower().endswith(extensions)]

# Перевірка
if count > len(images):
    raise ValueError("Зображень менше, ніж потрібно перемістити")

# Випадковий вибір
selected = random.sample(images, count)

# Переміщення
for img in selected:
    shutil.move(
        os.path.join(source_dir, img),
        os.path.join(target_dir, img)
    )

print(f"Переміщено {count} зображень 🎉")
