import argparse
import json
import os
import tempfile
import uuid

import torch
from ultralytics import YOLO


def run_yolo(path, output_path=None):
    model = YOLO("app/assets/Tree_disseses_finder.pt")
    image_path = path

    if output_path is None:
        output_path = os.path.join(
            tempfile.gettempdir(), f"model_output_{uuid.uuid4().hex}.jpg"
        )

    device = "cuda" if torch.cuda.is_available() else "cpu"
    results = model(image_path, device=device)
    results[0].save(filename=output_path)

    class_name = "N/A"
    conf = 0.0
    xyxy = (0.0, 0.0, 0.0, 0.0)
    detections = []

    for r in results:
        cls_indices = r.boxes.cls.cpu().numpy()
        confs = r.boxes.conf.cpu().numpy()
        xyxy_coords = r.boxes.xyxy.cpu().numpy()

        for cls_idx, conf, xyxy in zip(cls_indices, confs, xyxy_coords):
            class_name = r.names[int(cls_idx)]
            xyxy = tuple(round(float(c), 1) for c in xyxy)
            conf = round(float(conf), 2)
            detections.append(
                {
                    "class_name": class_name,
                    "conf": conf,
                    "xyxy": list(xyxy),
                }
            )

    return output_path, class_name, conf, xyxy, detections


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("image_path")
    parser.add_argument("--output-path", default=None)
    args = parser.parse_args()

    try:
        output_path, class_name, conf, xyxy, detections = run_yolo(
            args.image_path, output_path=args.output_path
        )
        print(
            json.dumps(
                {
                    "ok": True,
                    "output_path": output_path,
                    "class_name": class_name,
                    "conf": conf,
                    "xyxy": list(xyxy),
                    "detections": detections,
                }
            )
        )
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        raise
