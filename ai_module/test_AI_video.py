from ultralytics import YOLO
import glob
import os
import cv2

model = YOLO("/media/auxidtex/Local Disk/Project Data/app/assets/Tree_disseses_finder.pt")  

save_dir = "output_images"
os.makedirs(save_dir, exist_ok=True)

video_paths = glob.glob("/media/auxidtex/Local Disk/Project Data/ai_module/Videos Unfiltered/packet2/disease/Nectria_Canker/*.mp4")
if len(video_paths) == 0:
    print("No videos found in the specified directory.")

for img_path in video_paths:
    # YOLO stream
    results = model(img_path, stream=True)

    cap = cv2.VideoCapture(img_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    name = os.path.splitext(os.path.basename(img_path))[0]
    out_path = os.path.join(save_dir, name + "_yolo.mp4")

    out = cv2.VideoWriter(
        out_path,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (w, h)
    )

    for r in results:
        frame = cv2.cvtColor(r.plot(), cv2.COLOR_RGB2BGR)
        out.write(frame)

    out.release()
    print(f"Saved video: {out_path}")
