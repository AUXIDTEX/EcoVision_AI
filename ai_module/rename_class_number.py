import os
import re

# Налаштування
labels_path = "ai_module/dataset/labels/val/" 
start_frame_num = 65  # Починати з frame_42

def safe_remap(path, start_num):
    # Словник заміни: '0' -> '3', '1' -> '4'
    mapping = {'0': '3', '1': '4'}
    
    files = [f for f in os.listdir(path) if f.endswith('.txt')]
    count = 0

    for file_name in files:
        # Витягуємо номер з назви файлу frame_XXX.txt
        match = re.search(r'(\d+)', file_name)
        if match:
            current_num = int(match.group(1))
            if current_num < start_num:
                continue
            
            file_path = os.path.join(path, file_name)
            
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            new_lines = []
            for line in lines:
                parts = line.strip().split()
                if not parts:
                    continue
                
                # Міняємо ТІЛЬКИ перший елемент (клас), якщо він є в словнику
                if parts[0] in mapping:
                    parts[0] = mapping[parts[0]]
                
                # Збираємо рядок назад з ідеальною точністю координат
                new_lines.append(" ".join(parts) + "\n")
            
            with open(file_path, 'w') as f:
                f.writelines(new_lines)
            
            count += 1

    print(f"✅ Готово! Оброблено файлів: {count}")
    print(f"Заміна: 0 -> 3, 1 -> 4. Координати не змінені.")

# Запуск
safe_remap(labels_path, start_frame_num)