from __future__ import annotations
import json
import logging
import os
import subprocess
from pathlib import Path

import static_ffmpeg
static_ffmpeg.add_paths()

from app.config import settings
from app.exceptions import FrameExtractionError, VideoValidationError
from app.storage import audio_dir, frames_dir
logger = logging.getLogger(__name__)
FFPROBE_BIN = os.getenv("FFPROBE_BIN", "ffprobe")
FFMPEG_BIN = os.getenv("FFMPEG_BIN", "ffmpeg")
def validate_video(video_path: str | Path, max_duration_seconds: float) -> dict:
    video_path = str(video_path)
    cmd = [
        FFPROBE_BIN,
        "-v", "error",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        video_path,
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except FileNotFoundError:
        raise VideoValidationError("ffprobe not found — install ffmpeg and ensure it is on PATH")
    except subprocess.TimeoutExpired:
        raise VideoValidationError("ffprobe timed out — file may be corrupt or too large")
    if proc.returncode != 0:
        raise VideoValidationError(
            f"ffprobe rejected the file: {proc.stderr[:500]}"
        )
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        raise VideoValidationError(f"ffprobe output is not valid JSON: {e}")
    streams = data.get("streams", [])
    video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)
    if video_stream is None:
        raise VideoValidationError("File contains no video stream")
    fmt = data.get("format", {})
    duration = float(fmt.get("duration", 0.0) or 0.0)
    if duration <= 0:
        duration = float(video_stream.get("duration", 0.0) or 0.0)
    if duration > max_duration_seconds:
        raise VideoValidationError(
            f"Video is {duration:.1f}s — maximum allowed is {max_duration_seconds:.0f}s"
        )
    if duration < 0.5:
        raise VideoValidationError(f"Video is too short ({duration:.2f}s)")
    fps_raw = video_stream.get("r_frame_rate", "0/1")
    try:
        num, den = fps_raw.split("/")
        fps = float(num) / float(den) if float(den) != 0 else 0.0
    except (ValueError, ZeroDivisionError):
        fps = 0.0
    width = video_stream.get("width")
    height = video_stream.get("height")
    if width and height and (width < 64 or height < 64):
        raise VideoValidationError(
            f"Video resolution {width}×{height} is too low (minimum 64×64)"
        )
    return {
        "duration": duration,
        "fps": fps,
        "width": width,
        "height": height,
        "codec": video_stream.get("codec_name"),
        "codec_long": video_stream.get("codec_long_name"),
        "has_audio": audio_stream is not None,
        "audio_codec": audio_stream.get("codec_name") if audio_stream else None,
        "file_size_bytes": int(fmt.get("size", 0) or 0),
        "bit_rate": int(fmt.get("bit_rate", 0) or 0),
        "container": fmt.get("format_name", "unknown"),
    }
def _compute_blur_score(frame_path: str) -> float:
    try:
        import cv2
        import numpy as np
        img = cv2.imread(frame_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return 1.0
        lap_var = float(cv2.Laplacian(img, cv2.CV_64F).var())
        return min(lap_var / 500.0, 1.0)
    except Exception:
        return 1.0
def extract_frames(
    video_path: str | Path,
    job_id: str,
    metadata: dict,
) -> list[dict]:
    video_path = str(video_path)
    out_dir = frames_dir(job_id)
    duration = metadata.get("duration") or 1.0
    target = settings.FRAME_SAMPLE_COUNT
    if duration <= target:
        fps_arg = "1"
    else:
        fps_arg = f"{target / duration:.6f}"
    output_pattern = str(out_dir / "frame_%04d.jpg")
    cmd = [
        FFMPEG_BIN,
        "-y",
        "-skip_frame", "nokey",
        "-i", video_path,
        "-vf", f"fps={fps_arg}",
        "-qscale:v", "2",
        "-vframes", str(int(target * 2)),
        output_pattern,
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if proc.returncode != 0:
            raise FrameExtractionError(f"ffmpeg frame extraction failed: {proc.stderr[:500]}")
    except subprocess.TimeoutExpired:
        raise FrameExtractionError("ffmpeg timed out during frame extraction")
    scene_pattern = str(out_dir / "scene_%04d.jpg")
    scene_cmd = [
        FFMPEG_BIN,
        "-y",
        "-i", video_path,
        "-vf", "select=gt(scene\\,0.35),setpts=N/FRAME_RATE/TB",
        "-qscale:v", "2",
        "-vframes", str(target // 2),
        scene_pattern,
    ]
    try:
        subprocess.run(scene_cmd, capture_output=True, text=True, timeout=60)
    except Exception:
        pass
    all_jpegs = sorted(
        p for p in out_dir.iterdir() if p.suffix == ".jpg"
    )
    step = duration / max(len(all_jpegs), 1)
    frames: list[dict] = []
    for i, fpath in enumerate(all_jpegs):
        blur = _compute_blur_score(str(fpath))
        frames.append({
            "path": str(fpath),
            "filename": fpath.name,
            "frame_index": i,
            "timestamp": round(i * step, 3),
            "blur_score": blur,
        })
    max_frames = int(target * 1.5)
    if len(frames) > max_frames:
        frames = sorted(frames, key=lambda f: f["blur_score"], reverse=True)[:max_frames]
    frames = sorted(frames, key=lambda f: f["frame_index"])
    for i, f in enumerate(frames):
        f["frame_index"] = i
    logger.info("Extracted %d frames for job=%s", len(frames), job_id)
    return frames
def extract_audio(video_path: str | Path, job_id: str) -> str | None:
    video_path = str(video_path)
    out_path = str(audio_dir(job_id) / "audio.wav")
    cmd = [
        FFMPEG_BIN,
        "-y",
        "-i", video_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        out_path,
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if proc.returncode == 0 and Path(out_path).exists():
            logger.debug("Extracted audio for job=%s → %s", job_id, out_path)
            return out_path
        logger.debug("No audio stream in video for job=%s", job_id)
        return None
    except Exception as e:
        logger.warning("Audio extraction failed for job=%s: %s", job_id, e)
        return None
