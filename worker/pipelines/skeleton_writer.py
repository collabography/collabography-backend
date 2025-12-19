"""스켈레톤 JSON 생성 및 검증 유틸"""


def create_dummy_skeleton_json(
    fps: float = 30.0,
    num_frames: int = 100,
    num_joints: int = 33,
) -> dict:
    """더미 스켈레톤 JSON 생성 (MVP용)"""
    frames = []
    for frame_idx in range(num_frames):
        time_sec = frame_idx / fps
        keypoints = []
        for joint_idx in range(num_joints):
            # 더미 좌표 (실제로는 pose 추출 결과)
            keypoints.append({
                "x": 0.0,
                "y": 0.0,
                "z": 0.0,
                "confidence": 1.0,
            })
        frames.append({
            "frame_idx": frame_idx,
            "time_sec": round(time_sec, 3),
            "keypoints": keypoints,
        })

    return {
        "meta": {
            "fps": fps,
            "num_frames": num_frames,
            "num_joints": num_joints,
            "pose_model": "dummy",
            "version": "1.0",
        },
        "frames": frames,
    }


def validate_skeleton_json(data: dict) -> tuple[bool, str | None]:
    """스켈레톤 JSON 검증"""
    if "meta" not in data:
        return False, "Missing 'meta' field"

    meta = data["meta"]
    required_meta = ["fps", "num_frames", "num_joints"]
    for key in required_meta:
        if key not in meta:
            return False, f"Missing 'meta.{key}' field"

    if "frames" not in data:
        return False, "Missing 'frames' field"

    frames = data["frames"]
    if len(frames) != meta["num_frames"]:
        return False, f"frames length ({len(frames)}) != num_frames ({meta['num_frames']})"

    for i, frame in enumerate(frames):
        if "keypoints" not in frame:
            return False, f"Frame {i} missing 'keypoints'"
        if len(frame["keypoints"]) != meta["num_joints"]:
            return False, f"Frame {i} keypoints length ({len(frame['keypoints'])}) != num_joints ({meta['num_joints']})"

    return True, None

