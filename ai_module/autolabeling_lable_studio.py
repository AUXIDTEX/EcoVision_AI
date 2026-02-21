import os
import json
import base64
import uuid
from io import BytesIO

import requests
import torch
from PIL import Image
from ultralytics import YOLO

try:
    from label_studio_sdk import LabelStudio
except Exception:
    LabelStudio = None

LABEL_STUDIO_URL = os.getenv("LABEL_STUDIO_URL", "http://localhost:8080")
LABEL_STUDIO_API_KEY = os.getenv("LABEL_STUDIO_API_KEY", "")
PROJECT_ID = int(os.getenv("PROJECT_ID", "12"))
MODEL_PATH = os.getenv("MODEL_PATH", "/workspace/app/assets/Tree_disseses_finder.pt")
MODEL_VERSION = os.getenv("MODEL_VERSION", "finder")
FROM_NAME = os.getenv("FROM_NAME", "label")
TO_NAME = os.getenv("TO_NAME", "image")
RESULT_TYPE = os.getenv("RESULT_TYPE", "rectanglelabels")

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Використовується пристрій: {device}")
model = YOLO(MODEL_PATH)


def _is_reachable(base_url: str, timeout: int = 5) -> bool:
    try:
        r = requests.get(f"{base_url.rstrip('/')}/api/version", timeout=timeout)
        return r.status_code == 200
    except Exception:
        return False


def _resolve_label_studio_url() -> str:
    primary = LABEL_STUDIO_URL.rstrip("/")
    if _is_reachable(primary):
        return primary

    fallback = "http://172.17.0.1:8080"
    if primary != fallback and _is_reachable(fallback):
        print(f"Попередження: {primary} недоступний, використовую fallback {fallback}")
        return fallback

    raise RuntimeError(
        f"Label Studio недоступний за URL: {primary}. "
        "Задайте правильний LABEL_STUDIO_URL (для Docker часто http://172.17.0.1:8080)."
    )


def _jwt_token_type(token: str) -> str | None:
    parts = token.split(".")
    if len(parts) != 3:
        return None
    try:
        payload = parts[1]
        payload += "=" * (-len(payload) % 4)
        raw = base64.urlsafe_b64decode(payload.encode("ascii")).decode("utf-8")
        data = json.loads(raw)
        return data.get("token_type")
    except Exception:
        return None


def _refresh_to_access(base_url: str, refresh_token: str) -> str | None:
    try:
        r = requests.post(
            f"{base_url}/api/token/refresh",
            json={"refresh": refresh_token},
            timeout=10,
        )
        if r.status_code != 200:
            return None
        return r.json().get("access")
    except Exception:
        return None


def _auth_candidates(base_url: str) -> list[str]:
    raw = LABEL_STUDIO_API_KEY.strip().strip('"').strip("'")
    if not raw:
        return []

    low = raw.lower()
    if low.startswith("token ") or low.startswith("bearer "):
        return [raw]

    headers = [f"Token {raw}", f"Bearer {raw}"]
    if _jwt_token_type(raw) == "refresh":
        access = _refresh_to_access(base_url, raw)
        if access:
            headers.insert(0, f"Bearer {access}")
    return headers


def download_image(task_image_url: str, base_url: str, auth_values: list[str]) -> Image.Image:
    full_url = f"{base_url}{task_image_url}" if task_image_url.startswith("/") else task_image_url

    last_resp = None
    for auth in auth_values:
        resp = requests.get(full_url, headers={"Authorization": auth}, timeout=30)
        if resp.status_code == 200:
            return Image.open(BytesIO(resp.content))
        last_resp = resp
        if resp.status_code != 401:
            resp.raise_for_status()

    if last_resp is not None:
        last_resp.raise_for_status()
    raise RuntimeError("Не вдалося завантажити зображення: відсутні auth заголовки")


def predict_for_image(img: Image.Image) -> dict:
    orig_w, orig_h = img.size
    yolo_result = model.predict(img, device=device)[0]

    regions = []
    best_score = 0.0

    for box in yolo_result.boxes:
        b = box.xyxyn[0].tolist()
        x, y, x2, y2 = b[0] * 100, b[1] * 100, b[2] * 100, b[3] * 100

        x = max(0.0, min(100.0, x))
        y = max(0.0, min(100.0, y))
        x2 = max(0.0, min(100.0, x2))
        y2 = max(0.0, min(100.0, y2))
        if x2 <= x or y2 <= y:
            continue

        conf = float(box.conf)
        best_score = max(best_score, conf)
        label_name = yolo_result.names[int(box.cls)]

        regions.append(
            {
                "id": str(uuid.uuid4()),
                "type": RESULT_TYPE,
                "from_name": FROM_NAME,
                "to_name": TO_NAME,
                "original_width": orig_w,
                "original_height": orig_h,
                "image_rotation": 0,
                "score": conf,
                "value": {
                    "x": x,
                    "y": y,
                    "width": x2 - x,
                    "height": y2 - y,
                    "rotation": 0,
                    "rectanglelabels": [label_name],
                },
            }
        )

    return {
        "model_version": MODEL_VERSION,
        "score": best_score,
        "result": regions,
    }


def push_predictions() -> None:
    if LabelStudio is None:
        raise RuntimeError("label_studio_sdk не встановлено")
    if not LABEL_STUDIO_API_KEY:
        raise RuntimeError("Порожній LABEL_STUDIO_API_KEY")

    resolved_url = _resolve_label_studio_url()
    client = LabelStudio(base_url=resolved_url, api_key=LABEL_STUDIO_API_KEY)
    auth_values = _auth_candidates(resolved_url)
    if not auth_values:
        raise RuntimeError("Не вдалося побудувати Authorization header з LABEL_STUDIO_API_KEY")

    pushed = 0
    failed = 0
    for task in client.tasks.list(project=PROJECT_ID, include=["id", "data"]):
        task_id = getattr(task, "id", None) or task.get("id")
        task_data = getattr(task, "data", None) or task.get("data", {})
        image_url = task_data.get("image")
        if not image_url:
            failed += 1
            continue

        try:
            image = download_image(image_url, resolved_url, auth_values)
            prediction = predict_for_image(image)
            client.predictions.create(task=task_id, **prediction)
            pushed += 1
        except Exception as e:
            failed += 1
            print(f"Task {task_id}: {e}")

    print(
        f"Готово. project_id={PROJECT_ID}, pushed={pushed}, failed={failed}, model_version={MODEL_VERSION}"
    )


if __name__ == "__main__":
    push_predictions()
