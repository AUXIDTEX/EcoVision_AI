from ultralytics import YOLO

def run_yolo(path):
    device = "cpu"
    model = YOLO("runs/detect/12s/weights/best.pt")  # наприклад yolo11m.pt
    image_path = path
    results = model(image_path)

    results[0].save(filename="model_output.jpg")

    return "model_output.jpg"
    