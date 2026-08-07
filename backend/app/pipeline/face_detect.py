from __future__ import annotations
import logging
from pathlib import Path
logger = logging.getLogger(__name__)
_mtcnn = None
_LOAD_ATTEMPTED = False
def _get_mtcnn():
    global _mtcnn, _LOAD_ATTEMPTED
    if _LOAD_ATTEMPTED:
        return _mtcnn
    _LOAD_ATTEMPTED = True
    try:
        import torch
        from facenet_pytorch import MTCNN
        device = 'cuda' if torch.cuda.is_available() else ('mps' if hasattr(torch.backends, "mps") and torch.backends.mps.is_available() else 'cpu')
        _mtcnn = MTCNN(keep_all=True, device=device, min_face_size=30)
        logger.info("Loaded MTCNN face detector on %s", device)
    except Exception as e:
        logger.warning("facenet_pytorch (MTCNN) unavailable: %s — skipping face detection", e)
        _mtcnn = None
    return _mtcnn
def detect_faces_in_frame(frame_path: str) -> tuple[bool, list[dict]]:
    mtcnn = _get_mtcnn()
    if mtcnn is None:
        return False, []
    try:
        from PIL import Image
        img = Image.open(frame_path).convert('RGB')
        boxes, probs = mtcnn.detect(img)
        if boxes is None:
            return False, []
        bboxes = []
        for box, prob in zip(boxes, probs):
            if prob is None or prob < 0.85:
                continue
            x1, y1, x2, y2 = box
            w = x2 - x1
            h = y2 - y1
            bboxes.append({
                "x": int(max(0, x1)),
                "y": int(max(0, y1)),
                "w": int(w),
                "h": int(h),
                "confidence": float(prob)
            })
        if not bboxes:
            return False, []
        return True, bboxes
    except Exception as e:
        logger.debug("Face detection error on %s: %s", frame_path, e)
        return False, []
def detect_faces_batch(
    frames: list[dict],
    progress_callback=None,
) -> list[dict]:
    total = len(frames)
    for i, frame in enumerate(frames):
        has_face, bboxes = detect_faces_in_frame(frame["path"])
        frame["has_face"] = has_face
        frame["face_bboxes"] = bboxes
        frame["face_count"] = len(bboxes)
        if progress_callback and i % 5 == 0:
            progress_callback(i, total)
    face_count = sum(1 for f in frames if f["has_face"])
    logger.info(
        "Face detection complete: %d/%d frames contain faces", face_count, total
    )
    return frames
