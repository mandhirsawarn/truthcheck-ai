from __future__ import annotations
import logging
from typing import Any
import numpy as np
from scipy.ndimage import median_filter
from app.config import settings
from app.storage import frame_url, thumb_url
logger = logging.getLogger(__name__)
EVIDENCE_FRAME_COUNT = 5
TEMPORAL_SMOOTH_WINDOW = 3
def _smooth_scores(scores: list[float], window: int = TEMPORAL_SMOOTH_WINDOW) -> list[float]:
    if len(scores) <= 1:
        return scores
    arr = np.array(scores, dtype=float)
    smoothed = median_filter(arr, size=window, mode="nearest")
    return smoothed.tolist()
def _classify(score: float) -> str:
    if score >= settings.THRESHOLD_AI_GENERATED:
        return "likely_ai_generated"
    if score <= settings.THRESHOLD_AUTHENTIC:
        return "likely_authentic"
    return "inconclusive"
def _build_explanation_bullets(
    verdict: str,
    scored_frames: list[dict],
    spatial_mean: float,
    frequency_mean: float,
    temporal_mean: float,
    compression_mean: float,
    metadata: dict,
) -> list[str]:
    bullets: list[str] = []
    n = len(scored_frames)
    bullets.append(
        f"Analyzed {n} sampled frames over "
        f"{metadata.get('duration', 0):.1f}s at "
        f"{metadata.get('fps', 0):.1f} fps "
        f"({metadata.get('width')}×{metadata.get('height')}, {metadata.get('codec', 'unknown')} codec)"
    )
    high_spatial = [f for f in scored_frames if f.get("spatial_score", 0) > 0.65]
    if high_spatial:
        ts_list = ", ".join(f"{f['timestamp']:.1f}s" for f in high_spatial[:5])
        bullets.append(
            f"Spatial CNN (deepfake classifier): {len(high_spatial)}/{n} frames exceeded "
            f"confidence threshold — timestamps: {ts_list} "
            f"(mean score {spatial_mean * 100:.1f}%)"
        )
    else:
        bullets.append(
            f"Spatial CNN: No frames exceeded the detection threshold "
            f"(mean score {spatial_mean * 100:.1f}%)"
        )
    if settings.ENABLE_FREQUENCY_ANALYSIS:
        high_freq = [f for f in scored_frames if f.get("frequency_score", 0) > 0.5]
        if high_freq:
            bullets.append(
                f"Frequency analysis: {len(high_freq)}/{n} frames show anomalous spectral "
                f"distribution — GAN/diffusion models produce characteristic peaks in the "
                f"mid-frequency range not present in camera-captured footage "
                f"(mean anomaly score {frequency_mean * 100:.1f}%)"
            )
        else:
            bullets.append(
                f"Frequency analysis: Power spectral distribution within natural 1/f range "
                f"(mean anomaly score {frequency_mean * 100:.1f}%)"
            )
    if settings.ENABLE_TEMPORAL_ANALYSIS:
        high_temp = [f for f in scored_frames if f.get("temporal_score", 0) > 0.5]
        if high_temp:
            ts_list = ", ".join(f"{f['timestamp']:.1f}s" for f in high_temp[:3])
            bullets.append(
                f"Temporal consistency: {len(high_temp)}/{n} frames show anomalous inter-frame "
                f"motion patterns at {ts_list} — synthetic video generators often produce "
                f"unnatural flicker or unnaturally static regions across frames "
                f"(mean inconsistency {temporal_mean * 100:.1f}%)"
            )
        else:
            bullets.append(
                f"Temporal consistency: Frame-to-frame motion patterns are within expected "
                f"natural range (mean inconsistency {temporal_mean * 100:.1f}%)"
            )
    if settings.ENABLE_COMPRESSION_ANALYSIS:
        high_comp = [f for f in scored_frames if f.get("compression_score", 0) > 0.4]
        if high_comp:
            bullets.append(
                f"Compression artifact analysis: {len(high_comp)}/{n} frames show DCT block "
                f"boundary patterns inconsistent with genuine camera footage — AI-generated "
                f"content often has mismatched compression artifact profiles "
                f"(mean anomaly {compression_mean * 100:.1f}%)"
            )
        else:
            bullets.append(
                f"Compression artifact analysis: Block boundary patterns within expected "
                f"natural range (mean anomaly {compression_mean * 100:.1f}%)"
            )
    face_frames = sum(1 for f in scored_frames if f.get("has_face", False))
    if face_frames > 0:
        bullets.append(
            f"Face detection: {face_frames}/{n} frames contain detectable faces — "
            "face-region frames were weighted higher in the spatial CNN stream"
        )
    else:
        bullets.append(
            "Face detection: No faces detected in any sampled frame — the spatial "
            "classifiers are trained on cropped faces, so this result falls back to "
            "full-frame inference and should be treated as lower-confidence"
        )
    final_score_pct = (
        settings.WEIGHT_SPATIAL * spatial_mean +
        settings.WEIGHT_FREQUENCY * frequency_mean +
        settings.WEIGHT_TEMPORAL * temporal_mean +
        settings.WEIGHT_COMPRESSION * compression_mean
    ) * 100
    if verdict == "likely_ai_generated":
        bullets.append(
            f"Conclusion: Ensemble score {final_score_pct:.1f}% exceeds the "
            f"{settings.THRESHOLD_AI_GENERATED * 100:.0f}% threshold for AI-generated classification. "
            "The combined signal across spatial, frequency, and temporal streams strongly "
            "indicates synthetic generation or manipulation."
        )
    elif verdict == "likely_authentic":
        bullets.append(
            f"Conclusion: Ensemble score {final_score_pct:.1f}% is below the "
            f"{settings.THRESHOLD_AUTHENTIC * 100:.0f}% threshold. "
            "No significant synthetic artifacts detected across any signal stream."
        )
    else:
        bullets.append(
            f"Conclusion: Ensemble score {final_score_pct:.1f}% falls in the inconclusive range "
            f"({settings.THRESHOLD_AUTHENTIC * 100:.0f}%–{settings.THRESHOLD_AI_GENERATED * 100:.0f}%). "
            "Mixed signals across streams — not enough evidence to confidently classify."
        )
    return bullets
def aggregate_ensemble(
    scored_frames: list[dict],
    metadata: dict,
    job_id: str,
) -> dict:
    if not scored_frames:
        raise ValueError("No scored frames provided to aggregator")
    raw_fusion = [f["fusion_score"] for f in scored_frames]
    smoothed_fusion = _smooth_scores(raw_fusion)
    for i, frame in enumerate(scored_frames):
        frame["fusion_score_smoothed"] = smoothed_fusion[i]
    face_weights = np.array([
        1.0 if f.get("has_face", False) else settings.NON_FACE_FRAME_WEIGHT
        for f in scored_frames
    ])
    blur_weights = np.array([max(f.get("blur_score", 1.0), 0.1) for f in scored_frames])
    blur_weights = blur_weights * face_weights
    blur_weights /= blur_weights.sum()
    def _weighted_mean(key: str) -> float:
        vals = np.array([f.get(key, 0.0) for f in scored_frames])
        return float(np.dot(vals, blur_weights))
    spatial_mean = _weighted_mean("spatial_score")
    frequency_mean = _weighted_mean("frequency_score")
    temporal_mean = _weighted_mean("temporal_score")
    compression_mean = _weighted_mean("compression_score")
    smoothed_arr = np.array(smoothed_fusion)
    final_score = float(np.dot(smoothed_arr, blur_weights))
    verdict = _classify(final_score)
    top_frames = sorted(
        scored_frames,
        key=lambda f: f.get("fusion_score_smoothed", 0.0),
        reverse=True,
    )[:EVIDENCE_FRAME_COUNT]
    evidence_frame_urls = [
        frame_url(job_id, f["filename"]) for f in top_frames
    ]
    explanation_bullets = _build_explanation_bullets(
        verdict=verdict,
        scored_frames=scored_frames,
        spatial_mean=spatial_mean,
        frequency_mean=frequency_mean,
        temporal_mean=temporal_mean,
        compression_mean=compression_mean,
        metadata=metadata,
    )
    logger.info(
        "Aggregation complete: verdict=%s confidence=%.1f%% "
        "(spatial=%.1f%% freq=%.1f%% temp=%.1f%% comp=%.1f%%)",
        verdict,
        final_score * 100,
        spatial_mean * 100,
        frequency_mean * 100,
        temporal_mean * 100,
        compression_mean * 100,
    )
    return {
        "verdict": verdict,
        "confidence": round(final_score * 100, 2),
        "spatial_confidence": round(spatial_mean * 100, 2),
        "frequency_confidence": round(frequency_mean * 100, 2),
        "temporal_confidence": round(temporal_mean * 100, 2),
        "compression_confidence": round(compression_mean * 100, 2),
        "explanation_bullets": explanation_bullets,
        "evidence_frame_urls": evidence_frame_urls,
    }
