import os
from pathlib import Path

def rename_images_sequential(folder_path, prefix="frame", start=1):
    """
    Перейменовує всі зображення у папці послідовно
    
    Args:
        folder_path: шлях до папки з картинками
        prefix: префікс для імені (за замовчуванням "frame")
        start: з якого номера починати (за замовчуванням 1)
    """
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"❌ Папка не існує: {folder_path}")
        return
    
    # Розширення зображень
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp', '.txt'}
    
    # Знаходимо всі зображення
    images = sorted([f for f in folder.iterdir() 
                     if f.is_file() and f.suffix.lower() in image_extensions])
    
    if not images:
        print(f"⚠️ Не знайдено зображень у папці")
        return
    
    print(f"✓ Знайдено {len(images)} зображень")
    
    # Перейменовуємо у дві фази (щоб уникнути конфліктів імен)
    temp_names = []
    
    # Фаза 1: тимчасові імена
    for i, img in enumerate(images):
        temp_name = folder / f"temp_{i}{img.suffix}"
        img.rename(temp_name)
        temp_names.append((temp_name, img.suffix))
    
    # Фаза 2: фінальні імена
    for i, (temp_img, ext) in enumerate(temp_names, start=start):
        new_name = folder / f"{prefix}_{i}{ext}"
        temp_img.rename(new_name)
        print(f"{prefix}_{i}{ext}")
    
    print(f"\n✓ Готово! Перейменовано {len(images)} файлів")

# Використання
folder_path = "/media/auxidtex/Local Disk/Project Data/ai_module/small_dataset_13_02_26/dataset/labels/train"
rename_images_sequential(folder_path, prefix="frame", start=234)