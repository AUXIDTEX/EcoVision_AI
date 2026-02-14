import os
import re
from pathlib import Path

def get_file_number(path):
    # Шукає число в назві файлу
    match = re.search(r'(\d+)', path.name)
    return int(match.group(1)) if match else 0

def rename_images_sequential(folder_path, prefix="frame", start=1):
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"❌ Папка не існує: {folder_path}")
        return
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp', '.txt'}
    
    # КЛЮЧОВИЙ МОМЕНТ: Сортуємо за числом у назві, а не за алфавітом
    all_files = [f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in image_extensions]
    files = sorted(all_files, key=get_file_number)
    
    if not files:
        print(f"⚠️ Не знайдено файлів у папці")
        return
    
    print(f"✓ Знайдено {len(files)} файлів. Сортування за числами виконано.")
    
    temp_names = []
    # Фаза 1: Тимчасові імена (щоб не перезаписати існуючі)
    for i, file in enumerate(files):
        temp_name = folder / f"temp_{i}{file.suffix}"
        file.rename(temp_name)
        temp_names.append((temp_name, file.suffix))
    
    # Фаза 2: Фінальні імена
    for i, (temp_file, ext) in enumerate(temp_names, start=start):
        new_name = folder / f"{prefix}_{i}{ext}"
        temp_file.rename(new_name)
        print(f"Перейменовано: {temp_file.name} -> {new_name.name}")
    
    print(f"\n✓ Готово! Перейменовано {len(files)} файлів.")

# Використання
folder_path = "/media/auxidtex/Local Disk/Project Data/ai_module/Frames/packet1/temp"
rename_images_sequential(folder_path, prefix="frame", start=65)