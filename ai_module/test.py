import cv2

# Шлях до файлу зображення та TXT
image_path = "ai_module/dataset/images/train/frame_8.jpg"
txt_path = "ai_module/dataset/labels/train/frame_8.txt"

# Читаємо картинку
img = cv2.imread(image_path)
h, w, _ = img.shape

# Читаємо TXT
with open(txt_path, "r") as f:
    lines = f.readlines()

for line in lines:
    parts = line.strip().split()
    cls, x_center, y_center, bw, bh = map(float, parts)
    
    # Переводимо з відсотків у пікселі
    x_center *= w
    y_center *= h
    bw *= w
    bh *= h

    # Вираховуємо координати верхнього лівого і нижнього правого кутів
    x1 = int(x_center - bw / 2)
    y1 = int(y_center - bh / 2)
    x2 = int(x_center + bw / 2)
    y2 = int(y_center + bh / 2)

    # Малюємо бокс
    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.putText(img, str(int(cls)), (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)

# Показуємо картинку
cv2.imshow("image", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
