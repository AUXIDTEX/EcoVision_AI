from ultralytics import YOLO

def run_yolo(path):
    model = YOLO("runs/detect/databal_small_obj_1024px_yolov8n/weights/best.pt")
    image_path = path
    results = model(image_path)

    results[0].save(filename="model_output.jpg")

    class_name = "N/A"
    conf = 0.0
    xyxy = (0, 0, 0, 0)

    for r in results:
        cls_indices = r.boxes.cls.cpu().numpy()
        confs = r.boxes.conf.cpu().numpy()
        xyxy_coords = r.boxes.xyxy.cpu().numpy()

        for cls_idx, conf, xyxy in zip(cls_indices, confs, xyxy_coords):
            class_name = r.names[int(cls_idx)]
            xyxy = tuple(round(float(c), 1) for c in xyxy)  
            conf = round(float(conf), 2)
            print(class_name, conf, xyxy)



    return "model_output.jpg", class_name, conf, xyxy