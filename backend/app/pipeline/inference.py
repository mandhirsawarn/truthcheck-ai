from __future__ import annotations
import logging
import os
from pathlib import Path
from typing import Any
import numpy as np
from PIL import Image
from app.config import settings
logger = logging.getLogger(__name__)
class LocalModelPipeline:
    def __init__(self, checkpoint_path: str, device: str):
        import torch
        from torchvision import transforms
        self.device = torch.device(device if device != "auto" else "cpu")
        import timm
        self.base_model = timm.create_model("efficientnet_b0", pretrained=False, num_classes=2)
        ckpt = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
        self.base_model.load_state_dict(ckpt["model_state_dict"])
        self.base_model.to(self.device)
        self.base_model.eval()
        class DummyConfig:
            id2label = {0: "Fake", 1: "Real"}
        class DummyModel:
            config = DummyConfig()
        self.model_attr = DummyModel()
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ])
    @property
    def model(self):
        return self.model_attr
    def __call__(self, inputs, batch_size=16, top_k=None):
        import torch
        is_list = isinstance(inputs, list)
        if not is_list:
            inputs = [inputs]
        all_results = []
        with torch.no_grad():
            for i in range(0, len(inputs), batch_size):
                batch_inputs = inputs[i:i + batch_size]
                tensors = []
                for item in batch_inputs:
                    if isinstance(item, str):
                        from PIL import Image
                        img = Image.open(item).convert("RGB")
                    else:
                        img = item.convert("RGB")
                    tensors.append(self.transform(img))
                batch_tensor = torch.stack(tensors).to(self.device)
                logits = self.base_model(batch_tensor)
                probs = torch.softmax(logits, dim=1)
                for p in probs:
                    res = [
                        {"label": "Fake", "score": float(p[0])},
                        {"label": "Real", "score": float(p[1])}
                    ]
                    all_results.append(res)
        return all_results if is_list else all_results[0]
_classifiers: dict[str, Any] = {}
def _detect_device() -> str:
    if settings.MODEL_DEVICE != "auto":
        return settings.MODEL_DEVICE
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda"
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
    except ImportError:
        pass
    return "cpu"
def _load_classifiers() -> dict[str, Any]:
    global _classifiers
    if _classifiers:
        return _classifiers
    device = _detect_device()
    device_arg = 0 if device == "cuda" else (-1 if device == "cpu" else device)
    candidates = [settings.MODEL_NAME, settings.FALLBACK_MODEL_NAME]
    for model_name in candidates:
        try:
            if model_name == "local-efficientnet-b0":
                logger.info("Loading local deepfake classifier: %s (device=%s)", model_name, device)
                checkpoint_path = Path(__file__).resolve().parents[3] / "training" / "checkpoints" / "best_model.pt"
                if not checkpoint_path.exists():
                    logger.warning("Local model checkpoint not found at %s", checkpoint_path)
                    continue
                clf = LocalModelPipeline(str(checkpoint_path), device)
                id2label = getattr(getattr(clf, "model", None), "config", None)
                id2label = getattr(id2label, "id2label", {}) if id2label is not None else {}
                logger.info("Loaded %s — id2label=%s", model_name, id2label)
                _classifiers[model_name] = clf
            else:
                from transformers import pipeline as hf_pipeline
                logger.info("Loading deepfake classifier: %s (device=%s)", model_name, device)
                clf = hf_pipeline("image-classification", model=model_name, device=device_arg)
                id2label = getattr(getattr(clf, "model", None), "config", None)
                id2label = getattr(id2label, "id2label", {}) if id2label is not None else {}
                logger.info("Loaded %s — id2label=%s", model_name, id2label)
                _classifiers[model_name] = clf
        except Exception as exc:
            logger.warning("Failed to load model %s: %s", model_name, exc)
    if not _classifiers:
        raise RuntimeError("Could not load any deepfake detection model")
    return _classifiers
def get_loaded_model_version() -> str:
    if not _classifiers:
        return "unknown"
    return "+".join(sorted(_classifiers.keys()))
def _fake_score_from_predictions(predictions: list[dict]) -> float:
    for pred in predictions:
        label = str(pred.get("label", "")).lower()
        if any(k in label for k in ("fake", "deepfake", "ai", "synthetic", "generated")):
            return float(pred["score"])
    for pred in predictions:
        label = str(pred.get("label", "")).lower()
        if any(k in label for k in ("real", "authentic", "genuine", "original")):
            return 1.0 - float(pred["score"])
    logger.warning(
        "Could not map any label to fake/real in %s — defaulting to 0.5 "
        "(this model's labels aren't recognized; check MODEL_FAKE_GAMMA / id2label log)",
        predictions,
    )
    return 0.5
def _largest_face_bbox(face_bboxes: list[dict]) -> dict | None:
    if not face_bboxes:
        return None
    return max(face_bboxes, key=lambda b: b["w"] * b["h"])
def _load_classifier_input(frame: dict) -> "Image.Image | str":
    path = frame["path"]
    bbox = _largest_face_bbox(frame.get("face_bboxes") or [])
    if bbox is None:
        return path
    try:
        img = Image.open(path).convert("RGB")
    except Exception as e:
        logger.debug("Failed to open frame %s for cropping: %s", path, e)
        return path
    w, h = img.size
    margin = settings.FACE_CROP_MARGIN
    pad_x = bbox["w"] * margin
    pad_y = bbox["h"] * margin
    left = max(0, int(bbox["x"] - pad_x))
    top = max(0, int(bbox["y"] - pad_y))
    right = min(w, int(bbox["x"] + bbox["w"] + pad_x))
    bottom = min(h, int(bbox["y"] + bbox["h"] + pad_y))
    if right <= left or bottom <= top:
        return path
    return img.crop((left, top, right, bottom))
def _score_spatial_batch(frames: list[dict]) -> list[float]:
    classifiers = _load_classifiers()
    inputs = [_load_classifier_input(f) for f in frames]
    n = len(frames)
    per_model_scores: dict[str, list[float]] = {}
    for model_name, classifier in classifiers.items():
        try:
            all_predictions = classifier(inputs, batch_size=16, top_k=None)
            per_model_scores[model_name] = [
                _fake_score_from_predictions(preds) for preds in all_predictions
            ]
        except Exception as e:
            logger.warning(
                "Batch CNN inference failed for %s, falling back to per-frame: %s",
                model_name, e,
            )
            scores = []
            for item in inputs:
                try:
                    preds = classifier(item, top_k=None)
                    scores.append(_fake_score_from_predictions(preds))
                except Exception:
                    scores.append(0.5)
            per_model_scores[model_name] = scores
    if not per_model_scores:
        return [0.5] * n
    gammas = settings.MODEL_FAKE_GAMMA
    combined: list[float] = []
    for i in range(n):
        calibrated = []
        for model_name, scores in per_model_scores.items():
            gamma = gammas.get(model_name, 1.0)
            calibrated.append(float(np.clip(scores[i], 0.0, 1.0) ** gamma))
        combined.append(float(np.mean(calibrated)))
    return combined
def _natural_spectrum_reference(n_bins: int) -> np.ndarray:
    freqs = np.arange(1, n_bins + 1, dtype=float)
    return 1.0 / (freqs ** 2.0)
def _radial_average(psd_2d: np.ndarray) -> np.ndarray:
    h, w = psd_2d.shape
    cy, cx = h // 2, w // 2
    y, x = np.ogrid[-cy:h - cy, -cx:w - cx]
    r = np.sqrt(x * x + y * y).astype(int)
    max_r = min(cy, cx)
    radial = np.array([psd_2d[r == i].mean() if np.any(r == i) else 0.0 for i in range(max_r)])
    return radial
def _frequency_anomaly_score(frame_path: str) -> float:
    try:
        import cv2
        img = cv2.imread(frame_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return 0.5
        img = cv2.resize(img, (224, 224))
        f = np.fft.fft2(img.astype(float))
        f_shift = np.fft.fftshift(f)
        psd = np.abs(f_shift) ** 2
        radial = _radial_average(psd)
        if len(radial) < 4:
            return 0.5
        radial = radial / (radial.sum() + 1e-10)
        ref = _natural_spectrum_reference(len(radial))
        ref = ref / (ref.sum() + 1e-10)
        divergence = float(np.abs(radial - ref).sum())
        score = min(max((divergence - 1.0) / 0.5, 0.0), 1.0)
        return float(score)
    except Exception as e:
        logger.debug("Frequency analysis error on %s: %s", frame_path, e)
        return 0.5
def _score_frequency_batch(frames: list[dict]) -> list[float]:
    return [_frequency_anomaly_score(f["path"]) for f in frames]
def _temporal_inconsistency_score(frames: list[dict]) -> list[float]:
    if len(frames) < 2:
        return [0.5] * len(frames)
    try:
        import cv2
        def _load_gray_small(path: str) -> np.ndarray | None:
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                return None
            return cv2.resize(img, (112, 112)).astype(float)
        images = [_load_gray_small(f["path"]) for f in frames]
        diffs: list[float] = []
        for i in range(len(images) - 1):
            a, b = images[i], images[i + 1]
            if a is None or b is None:
                diffs.append(0.0)
                continue
            diff = np.abs(b - a)
            diffs.append(float(diff.mean()))
        if not diffs:
            return [0.5] * len(frames)
        diffs_arr = np.array(diffs)
        flicker = diffs_arr.max() / (diffs_arr.mean() + 1e-6)
        score = min(max((flicker - 2.0) / 3.0, 0.0), 1.0)
        return [float(score)] * len(frames)
    except Exception as e:
        logger.debug("Temporal analysis error: %s", e)
        return [0.5] * len(frames)
def _compression_artifact_score(frame_path: str) -> float:
    try:
        import cv2
        img = cv2.imread(frame_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return 0.5
        h, w = img.shape
        img_float = img.astype(float)
        block_h_grads = []
        for col in range(8, w, 8):
            grad = np.abs(img_float[:, col] - img_float[:, col - 1]).mean()
            block_h_grads.append(grad)
        block_v_grads = []
        for row in range(8, h, 8):
            grad = np.abs(img_float[row, :] - img_float[row - 1, :]).mean()
            block_v_grads.append(grad)
        if not block_h_grads and not block_v_grads:
            return 0.5
        mid_h_grads = []
        for col in range(4, w, 8):
            grad = np.abs(img_float[:, col] - img_float[:, col - 1]).mean()
            mid_h_grads.append(grad)
        block_mean = np.mean(block_h_grads + block_v_grads)
        mid_mean = np.mean(mid_h_grads) if mid_h_grads else block_mean
        ratio = (block_mean / (mid_mean + 1e-6))
        if ratio < 1.1:
            score = (1.1 - ratio) / 1.1
        elif ratio > 3.5:
            score = min((ratio - 3.5) / 3.5, 1.0)
        else:
            score = 0.1
        return float(score)
    except Exception as e:
        logger.debug("Compression analysis error on %s: %s", frame_path, e)
        return 0.5
def _score_compression_batch(frames: list[dict]) -> list[float]:
    return [_compression_artifact_score(f["path"]) for f in frames]
def _score_audio_visual_sync(frames: list[dict], audio_path: str | None) -> list[float]:
    if not settings.ENABLE_AUDIO_ANALYSIS or audio_path is None:
        return [0.0] * len(frames)
    try:
        import librosa
        y, sr = librosa.load(audio_path, sr=16000, mono=True, duration=30.0)
        frame_length = int(sr * 0.1)
        hop_length = frame_length // 2
        rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
        if rms.std() < 1e-6:
            return [0.25] * len(frames)
        rms_norm = (rms - rms.min()) / (rms.max() - rms.min() + 1e-6)
        n_frames = len(frames)
        indices = np.linspace(0, len(rms_norm) - 1, n_frames).astype(int)
        return [float(1.0 - rms_norm[i]) * 0.3 for i in indices]
    except Exception as e:
        logger.debug("Audio-visual sync analysis failed: %s", e)
        return [0.0] * len(frames)
def score_frames_ensemble(
    frames: list[dict],
    audio_path: str | None = None,
) -> list[dict]:
    if not frames:
        return []
    n = len(frames)
    logger.info("Running spatial CNN on %d frames", n)
    try:
        spatial_scores = _score_spatial_batch(frames)
    except Exception as e:
        logger.warning("Spatial CNN failed: %s — using 0.5 fallback", e)
        spatial_scores = [0.5] * n
    freq_scores: list[float]
    if settings.ENABLE_FREQUENCY_ANALYSIS:
        logger.info("Running frequency analysis on %d frames", n)
        freq_scores = _score_frequency_batch(frames)
    else:
        freq_scores = [0.0] * n
    temp_scores: list[float]
    if settings.ENABLE_TEMPORAL_ANALYSIS:
        logger.info("Running temporal consistency analysis on %d frames", n)
        temp_scores = _temporal_inconsistency_score(frames)
    else:
        temp_scores = [0.0] * n
    comp_scores: list[float]
    if settings.ENABLE_COMPRESSION_ANALYSIS:
        logger.info("Running compression artifact analysis on %d frames", n)
        comp_scores = _score_compression_batch(frames)
    else:
        comp_scores = [0.0] * n
    av_sync_scores = _score_audio_visual_sync(frames, audio_path)
    w_s = settings.WEIGHT_SPATIAL
    w_f = settings.WEIGHT_FREQUENCY
    w_t = settings.WEIGHT_TEMPORAL
    w_c = settings.WEIGHT_COMPRESSION
    w_a = getattr(settings, "WEIGHT_AUDIO", 0.1) if settings.ENABLE_AUDIO_ANALYSIS else 0.0
    scored: list[dict] = []
    for i, frame in enumerate(frames):
        blur = frame.get("blur_score", 1.0)
        face_boost = 1.1 if frame.get("has_face", False) else 0.9
        a_score = av_sync_scores[i] if i < len(av_sync_scores) else 0.0
        fusion = (
            w_s * spatial_scores[i] * blur * face_boost +
            w_f * freq_scores[i] +
            w_t * temp_scores[i] +
            w_c * comp_scores[i] +
            w_a * a_score
        )
        weight_sum = w_s * blur * face_boost + w_f + w_t + w_c + w_a
        fusion = fusion / (weight_sum + 1e-10)
        fusion = float(np.clip(fusion, 0.0, 1.0))
        scored.append({
            **frame,
            "spatial_score": float(spatial_scores[i]),
            "frequency_score": float(freq_scores[i]),
            "temporal_score": float(temp_scores[i]),
            "compression_score": float(comp_scores[i]),
            "audio_sync_score": float(av_sync_scores[i]) if i < len(av_sync_scores) else 0.0,
            "fusion_score": fusion,
        })
    return scored
