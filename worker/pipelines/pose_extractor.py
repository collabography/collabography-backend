"""Lightweight MediaPipe pose extraction pipeline (COCO17 normalized)."""

from __future__ import annotations

import json
import tempfile
import urllib.request
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from mediapipe import Image, ImageFormat
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from tqdm import tqdm

# -----------------------------
# COCO17 names (target output)
# -----------------------------
JOINT_NAMES = [
    "nose",
    "l_eye",
    "r_eye",
    "l_ear",
    "r_ear",
    "l_shoulder",
    "r_shoulder",
    "l_elbow",
    "r_elbow",
    "l_wrist",
    "r_wrist",
    "l_hip",
    "r_hip",
    "l_knee",
    "r_knee",
    "l_ankle",
    "r_ankle",
]
name2i = {n: i for i, n in enumerate(JOINT_NAMES)}
J = len(JOINT_NAMES)

# MediaPipe Pose 33 landmark indices -> map to COCO17
MP_TO_COCO17 = {
    "nose": 0,
    "l_eye": 2,
    "r_eye": 5,
    "l_ear": 7,
    "r_ear": 8,
    "l_shoulder": 11,
    "r_shoulder": 12,
    "l_elbow": 13,
    "r_elbow": 14,
    "l_wrist": 15,
    "r_wrist": 16,
    "l_hip": 23,
    "r_hip": 24,
    "l_knee": 25,
    "r_knee": 26,
    "l_ankle": 27,
    "r_ankle": 28,
}

L_HIP, R_HIP = name2i["l_hip"], name2i["r_hip"]
L_SH, R_SH = name2i["l_shoulder"], name2i["r_shoulder"]

MODEL_URL_LITE = (
    "https://storage.googleapis.com/mediapipe-models/"
    "pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task"
)


def ensure_model(model_path: str | Path | None = None) -> Path:
    """Download pose model if missing and return its path."""
    target = Path(model_path) if model_path else Path(tempfile.gettempdir()) / "pose_landmarker.task"
    if target.exists():
        return target
    target.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(MODEL_URL_LITE, target)  # nosec - controlled URL
    return target


def get_video_meta(path: str) -> tuple[float, int, int, int]:
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise RuntimeError(f"failed to open: {path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return float(fps), frame_count, width, height


def normalize_pose(kps_norm: np.ndarray) -> np.ndarray:
    """Hip-center translation + shoulder-hip scale normalization."""
    hip_center = 0.5 * (kps_norm[L_HIP] + kps_norm[R_HIP])
    kps = kps_norm - hip_center[None, :]
    shoulder_center = 0.5 * (kps_norm[L_SH] + kps_norm[R_SH])
    scale = np.linalg.norm(shoulder_center - hip_center)
    if scale < 1e-6:
        scale = 1.0
    return kps / scale


def extract_pose_to_json(
    video_path: str,
    model_path: str | Path | None = None,
    conf_thr: float = 0.2,
) -> dict[str, Any]:
    """Run MediaPipe PoseLandmarker and return JSON-serializable result."""
    model_file = ensure_model(model_path)
    fps, n_raw, _w, _h = get_video_meta(video_path)

    base_options = python.BaseOptions(model_asset_path=str(model_file))
    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        num_poses=1,
    )

    cap = cv2.VideoCapture(video_path)
    frames_out: list[dict[str, Any]] = []
    frame_idx = 0

    with vision.PoseLandmarker.create_from_options(options) as landmarker:
        pbar = tqdm(total=n_raw, desc="Pose extraction", leave=False)
        while True:
            ok, frame_bgr = cap.read()
            if not ok:
                break

            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            mp_image = Image(image_format=ImageFormat.SRGB, data=frame_rgb)

            timestamp_ms = int(round((frame_idx / fps) * 1000.0))
            result = landmarker.detect_for_video(mp_image, timestamp_ms)

            has_pose = (result.pose_landmarks is not None) and (len(result.pose_landmarks) > 0)

            kps_norm = np.zeros((J, 2), dtype=np.float32)
            conf = np.zeros((J,), dtype=np.float32)

            if has_pose:
                lm33 = result.pose_landmarks[0]  # 33 landmarks
                for jn in JOINT_NAMES:
                    mp_idx = MP_TO_COCO17[jn]
                    kp = lm33[mp_idx]
                    kps_norm[name2i[jn], 0] = float(kp.x)
                    kps_norm[name2i[jn], 1] = float(kp.y)
                    conf[name2i[jn]] = float(getattr(kp, "visibility", 1.0))

            kps_n = normalize_pose(kps_norm) if has_pose else kps_norm

            keypoints, pose_vec, valid_mask = [], [], []
            for j in range(J):
                x, y = float(kps_n[j, 0]), float(kps_n[j, 1])
                v = float(conf[j])
                keypoints.append({"x": x, "y": y, "z": 0.0, "visibility": v})
                pose_vec.extend([x, y, 0.0])
                valid_mask.append(1 if v >= conf_thr else 0)

            frames_out.append(
                {
                    "frame_idx": frame_idx,
                    "time_sec": frame_idx / float(fps),
                    "has_pose": bool(has_pose),
                    "keypoints": keypoints,
                    "pose_vec": pose_vec,
                    "valid_mask": valid_mask,
                }
            )

            frame_idx += 1
            pbar.update(1)

        pbar.close()

    cap.release()

    return {
        "meta": {
            "video_path": video_path,
            "fps": float(fps),
            "num_frames_raw": int(n_raw),
            "num_frames": int(len(frames_out)),
            "pose_model": "mediapipe_pose_landmarker_tasks_lite",
            "num_joints": J,
            "joints": JOINT_NAMES,
            "normalization": "hip_center + shoulder_hip_scale",
            "note": "COCO17 mapped from MP33; no fps resampling",
        },
        "frames": frames_out,
    }


def dump_json_to_bytes(data: dict[str, Any]) -> bytes:
    """Serialize JSON with utf-8 for upload."""
    return json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
