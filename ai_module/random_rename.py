import os
import random
import string
from pathlib import Path

def rename_images_random(folder_path, length=5):
    """
    Перейменовує всі зображення у папці на рандомні назви
    
    Args:
        folder_path: шлях до папки з картинками
        length: довжина нової назви (за замовчуванням 5)
    """
    # Розширення зображень
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
    
    folder = Path(folder_path)
    
    # Знаходимо всі зображення
    images = [f for f in folder.iterdir() 
              if f.is_file() and f.suffix.lower() in image_extensions]
    
    print(f"Знайдено {len(images)} зображень")
    
    # Генеруємо унікальні імена
    used_names = set()
    
    for img in images:
        extension = img.suffix
        
        # Генеруємо унікальне ім'я
        while True:
            new_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
            if new_name not in used_names:
                used_names.add(new_name)
                break
        
        new_path = img.parent / f"{new_name}{extension}"
        
        # Перейменовуємо
        img.rename(new_path)
        print(f"{img.name} -> {new_name}{extension}")
    
    print(f"\nГотово! Перейменовано {len(images)} файлів")

# Використання
folder_path = "//media//auxidtex//Local Disk//Project Data//ai_module//Frames//packet1//val"  # <- Змініть на свій шлях
rename_images_random(folder_path)