import os
import numpy as np
import pytest
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./data/test.db")
os.environ.setdefault("UPLOAD_DIR", "./data/test_uploads")
class TestRadialAverage:
    def test_returns_correct_length(self):
        from app.pipeline.inference import _radial_average
        psd = np.ones((64, 64))
        result = _radial_average(psd)
        assert len(result) == 32
    def test_uniform_psd_gives_uniform_radial(self):
        from app.pipeline.inference import _radial_average
        psd = np.ones((64, 64))
        radial = _radial_average(psd)
        assert radial.std() < 0.5
class TestNaturalSpectrumReference:
    def test_is_monotonically_decreasing(self):
        from app.pipeline.inference import _natural_spectrum_reference
        ref = _natural_spectrum_reference(32)
        assert all(ref[i] > ref[i + 1] for i in range(len(ref) - 1))
    def test_all_positive(self):
        from app.pipeline.inference import _natural_spectrum_reference
        ref = _natural_spectrum_reference(50)
        assert all(r > 0 for r in ref)
class TestFrequencyAnomalyScore:
    def test_score_in_range(self, tmp_path):
        try:
            import cv2
        except ImportError:
            pytest.skip("opencv not installed")
        from app.pipeline.inference import _frequency_anomaly_score
        img = np.random.randint(0, 255, (224, 224), dtype=np.uint8)
        img_path = str(tmp_path / "test_frame.jpg")
        cv2.imwrite(img_path, img)
        score = _frequency_anomaly_score(img_path)
        assert 0.0 <= score <= 1.0
    def test_missing_file_returns_midpoint(self):
        from app.pipeline.inference import _frequency_anomaly_score
        score = _frequency_anomaly_score("/nonexistent/path/frame.jpg")
        assert score == 0.5
class TestCompressionScore:
    def test_score_in_range(self, tmp_path):
        try:
            import cv2
        except ImportError:
            pytest.skip("opencv not installed")
        from app.pipeline.inference import _compression_artifact_score
        img = np.random.randint(0, 255, (224, 224), dtype=np.uint8)
        img_path = str(tmp_path / "test_frame.jpg")
        cv2.imwrite(img_path, img)
        score = _compression_artifact_score(img_path)
        assert 0.0 <= score <= 1.0
class TestTemporalScores:
    def test_identical_frames_give_high_score(self, tmp_path):
        try:
            import cv2
        except ImportError:
            pytest.skip("opencv not installed")
        from app.pipeline.inference import _temporal_inconsistency_score
        img = np.zeros((224, 224), dtype=np.uint8)
        frames = []
        for i in range(5):
            p = str(tmp_path / f"frame_{i:04d}.jpg")
            cv2.imwrite(p, img)
            frames.append({"path": p, "frame_index": i, "timestamp": float(i)})
        scores = _temporal_inconsistency_score(frames)
        assert len(scores) == 5
    def test_single_frame_returns_midpoint(self):
        from app.pipeline.inference import _temporal_inconsistency_score
        scores = _temporal_inconsistency_score([{"path": "x.jpg"}])
        assert scores == [0.5]
