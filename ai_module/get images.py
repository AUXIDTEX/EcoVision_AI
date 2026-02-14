import os
import glob
import subprocess
import shutil
import re
from tqdm import tqdm

input_folder = "ai_module/Videos Unfiltered/packet2/disease/Nectria Canker"
output_folder = "ai_module/Frames/packet2/big"
frame_step = 24

print("=" * 60)
print("🎬 ОБРОБКА ВІДЕО → КАДРИ")
print("=" * 60)

os.makedirs(output_folder, exist_ok=True)

# ============================================================================
# КРОК 1: ПЕРЕЙМЕНУВАННЯ ІСНУЮЧИХ ФАЙЛІВ
# ============================================================================
existing_files = glob.glob(os.path.join(output_folder, "*.jpg"))
existing_frames_proper = [f for f in existing_files if re.match(r".*frame_\d+\.jpg$", f)]
other_files = [f for f in existing_files if not re.match(r".*frame_\d+\.jpg$", f)]

if other_files:
    print(f"\n📝 Знайдено {len(other_files)} файлів зі старими назвами")
    
    max_num = 0
    for f in existing_frames_proper:
        match = re.search(r"frame_(\d+)\.jpg", os.path.basename(f))
        if match:
            max_num = max(max_num, int(match.group(1)))
    
    rename_counter = max_num + 1
    print(f"🔄 Перейменування файлів...")
    for old_path in tqdm(sorted(other_files), desc="Перейменування", unit="файл"):
        new_name = os.path.join(output_folder, f"frame_{rename_counter:06d}.jpg")
        os.rename(old_path, new_name)
        rename_counter += 1
    
    print(f"✅ Перейменовано до frame_{rename_counter-1:06d}.jpg\n")
    frame_counter = rename_counter
else:
    existing_frames = glob.glob(os.path.join(output_folder, "frame_*.jpg"))
    frame_numbers = []
    for f in existing_frames:
        match = re.search(r"frame_(\d+)\.jpg", os.path.basename(f))
        if match:
            frame_numbers.append(int(match.group(1)))
    
    frame_counter = max(frame_numbers) + 1 if frame_numbers else 1
    if frame_numbers:
        print(f"📊 Існуючих кадрів: {len(frame_numbers)}")

print(f"🔢 Початковий номер кадру: {frame_counter}\n")

# ============================================================================
# КРОК 2: ОБРОБКА ВІДЕО
# ============================================================================
videos = glob.glob(os.path.join(input_folder, "*.mp4"))

print(f"🎥 Знайдено відео: {len(videos)}\n")

if not videos:
    print(f"❌ Жодного відео не знайдено в '{input_folder}'")
    exit(1)

total_extracted = 0

for video_path in tqdm(videos, desc="📹 Обробка відео", unit="відео"):
    temp_folder = os.path.join(output_folder, "temp_frames")
    os.makedirs(temp_folder, exist_ok=True)

    cmd = (
        f'ffmpeg -i "{video_path}" -vf "select=not(mod(n\\,{frame_step}))" '
        f'-vsync vfr "{temp_folder}/frame_%06d.jpg" -hide_banner -loglevel error'
    )
    subprocess.run(cmd, shell=True)

    temp_frames = sorted(glob.glob(os.path.join(temp_folder, "frame_*.jpg")))
    
    for frame_path in temp_frames:
        new_name = os.path.join(output_folder, f"frame_{frame_counter:06d}.jpg")
        shutil.move(frame_path, new_name)
        frame_counter += 1
        total_extracted += 1

    shutil.rmtree(temp_folder)

# ============================================================================
# ПІДСУМОК
# ============================================================================
all_frames = glob.glob(os.path.join(output_folder, "frame_*.jpg"))
print("\n" + "=" * 60)
print(f"✅ ГОТОВО!")
print(f"📊 Витягнуто нових кадрів: {total_extracted}")
print(f"📊 Загальна кількість кадрів: {len(all_frames)}")
print(f"📁 Збережено в: {output_folder}")
print("=" * 60)