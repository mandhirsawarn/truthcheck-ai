import pytest
import numpy as np
import os
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./data/test.db")
os.environ.setdefault("UPLOAD_DIR", "./data/test_uploads")
def _make_frames(scores: list[float], has_face: bool = True) -> list[dict]:
    return [
        {
            "path": f"/tmp/frame_{i:04d}.jpg",
            "filename": f"frame_{i:04d}.jpg",
            "frame_index": i,
            "timestamp": float(i),
            "blur_score": 0.8,
            "has_face": has_face,
            "spatial_score": s,
            "frequency_score": s * 0.8,
            "temporal_score": s * 0.6,
            "compression_score": s * 0.4,
            "fusion_score": s,
            "face_bboxes": [],
            "face_count": 1 if has_face else 0,
        }
        for i, s in enumerate(scores)
    ]
class TestClassification:
    def test_likely_ai_generated(self):
        from app.config import settings
        from app.pipeline.aggregate import _classify
        assert _classify(settings.THRESHOLD_AI_GENERATED) == "likely_ai_generated"
        assert _classify(1.00) == "likely_ai_generated"
    def test_likely_authentic(self):
        from app.config import settings
        from app.pipeline.aggregate import _classify
        assert _classify(settings.THRESHOLD_AUTHENTIC) == "likely_authentic"
        assert _classify(0.00) == "likely_authentic"
    def test_inconclusive(self):
        from app.config import settings
        from app.pipeline.aggregate import _classify
        midpoint = (settings.THRESHOLD_AI_GENERATED + settings.THRESHOLD_AUTHENTIC) / 2
        assert _classify(midpoint) == "inconclusive"
        assert _classify(settings.THRESHOLD_AI_GENERATED - 1e-6) == "inconclusive"
        assert _classify(settings.THRESHOLD_AUTHENTIC + 1e-6) == "inconclusive"
class TestTemporalSmoothing:
    def test_smoothing_reduces_outliers(self):
        from app.pipeline.aggregate import _smooth_scores
        scores = [0.1, 0.1, 0.9, 0.1, 0.1]
        smoothed = _smooth_scores(scores, window=3)
        assert smoothed[2] < 0.9
    def test_smoothing_preserves_sustained_high(self):
        from app.pipeline.aggregate import _smooth_scores
        scores = [0.8, 0.85, 0.9, 0.85, 0.8]
        smoothed = _smooth_scores(scores)
        assert all(s > 0.75 for s in smoothed)
    def test_single_frame_returns_unchanged(self):
        from app.pipeline.aggregate import _smooth_scores
        assert _smooth_scores([0.7]) == [0.7]
    def test_empty_returns_empty(self):
        from app.pipeline.aggregate import _smooth_scores
        assert _smooth_scores([]) == []
class TestExplanationBullets:
    def test_ai_generated_explanation_contains_key_info(self):
        from app.pipeline.aggregate import _build_explanation_bullets
        frames = _make_frames([0.9, 0.85, 0.92])
        bullets = _build_explanation_bullets(
            verdict="likely_ai_generated",
            scored_frames=frames,
            spatial_mean=0.89,
            frequency_mean=0.70,
            temporal_mean=0.55,
            compression_mean=0.40,
            metadata={"duration": 3.0, "fps": 30.0, "width": 1920, "height": 1080, "codec": "h264"},
        )
        assert len(bullets) >= 4
        assert "3" in bullets[0]
        assert any("Spatial CNN" in b for b in bullets)
        assert any("Conclusion" in b for b in bullets)
    def test_authentic_explanation(self):
        from app.pipeline.aggregate import _build_explanation_bullets
        frames = _make_frames([0.1, 0.15, 0.12])
        bullets = _build_explanation_bullets(
            verdict="likely_authentic",
            scored_frames=frames,
            spatial_mean=0.12,
            frequency_mean=0.08,
            temporal_mean=0.05,
            compression_mean=0.04,
            metadata={"duration": 3.0, "fps": 24.0, "width": 1280, "height": 720, "codec": "h264"},
        )
        assert any("authentic" in b.lower() or "natural" in b.lower() for b in bullets)
    def test_no_faces_flags_lower_confidence(self):
        from app.pipeline.aggregate import _build_explanation_bullets
        frames = _make_frames([0.1, 0.15, 0.12], has_face=False)
        bullets = _build_explanation_bullets(
            verdict="likely_authentic",
            scored_frames=frames,
            spatial_mean=0.12,
            frequency_mean=0.08,
            temporal_mean=0.05,
            compression_mean=0.04,
            metadata={"duration": 3.0, "fps": 24.0, "width": 1280, "height": 720, "codec": "h264"},
        )
        assert any("lower-confidence" in b.lower() for b in bullets)
class TestAggregateEnsemble:
    def test_aggregate_ai_generated(self, tmp_path, monkeypatch):
        monkeypatch.setattr("app.storage.settings.PUBLIC_BASE_URL", "http://localhost:8000")
        monkeypatch.setattr("app.storage.settings.UPLOAD_DIR", tmp_path)
        from app.pipeline.aggregate import aggregate_ensemble
        frames = _make_frames([0.85, 0.90, 0.88, 0.92, 0.87])
        result = aggregate_ensemble(
            scored_frames=frames,
            metadata={"duration": 5.0, "fps": 30.0, "width": 1920, "height": 1080, "codec": "h264"},
            job_id="test-job-id",
        )
        assert result["verdict"] == "likely_ai_generated"
        assert result["confidence"] > 75.0
        assert len(result["explanation_bullets"]) >= 4
    def test_aggregate_authentic(self, tmp_path, monkeypatch):
        monkeypatch.setattr("app.storage.settings.PUBLIC_BASE_URL", "http://localhost:8000")
        monkeypatch.setattr("app.storage.settings.UPLOAD_DIR", tmp_path)
        from app.pipeline.aggregate import aggregate_ensemble
        frames = _make_frames([0.10, 0.12, 0.08, 0.11, 0.09])
        result = aggregate_ensemble(
            scored_frames=frames,
            metadata={"duration": 5.0, "fps": 30.0, "width": 1280, "height": 720, "codec": "h264"},
            job_id="test-job-id-2",
        )
        assert result["verdict"] == "likely_authentic"
        assert result["confidence"] < 35.0
    def test_aggregate_raises_on_empty(self, tmp_path):
        from app.pipeline.aggregate import aggregate_ensemble
        with pytest.raises(ValueError, match="No scored frames"):
            aggregate_ensemble(scored_frames=[], metadata={}, job_id="x")
    def test_non_face_frames_weighted_down(self, tmp_path, monkeypatch):
        monkeypatch.setattr("app.storage.settings.PUBLIC_BASE_URL", "http://localhost:8000")
        monkeypatch.setattr("app.storage.settings.UPLOAD_DIR", tmp_path)
        from app.pipeline.aggregate import aggregate_ensemble
        face_frames = _make_frames([0.05, 0.06, 0.04], has_face=True)
        noisy_no_face_frames = _make_frames([0.95, 0.97, 0.96], has_face=False)
        for i, f in enumerate(noisy_no_face_frames):
            f["frame_index"] = len(face_frames) + i
            f["filename"] = f"frame_{f['frame_index']:04d}.jpg"
        result = aggregate_ensemble(
            scored_frames=face_frames + noisy_no_face_frames,
            metadata={"duration": 6.0, "fps": 30.0, "width": 1280, "height": 720, "codec": "h264"},
            job_id="test-job-id-3",
        )
        assert result["verdict"] == "likely_authentic"
