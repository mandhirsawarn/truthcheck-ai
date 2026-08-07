import os
import pytest
from pydantic import ValidationError
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./data/test.db")
os.environ.setdefault("UPLOAD_DIR", "./data/test_uploads")
class TestUploadInitRequest:
    def test_valid_request(self):
        from app.schemas import UploadInitRequest
        req = UploadInitRequest(
        filename="test_video.mp4",
        file_size_bytes=1024 * 1024,
        mime_type="video/mp4",
)
assert req.filename == "test_video.mp4"
assert req.total_chunks is None
def test_rejects_empty_filename(self):
    from app.schemas import UploadInitRequest
    with pytest.raises(ValidationError):
        UploadInitRequest(filename="", file_size_bytes=1024, mime_type="video/mp4")
        def test_rejects_zero_size(self):
            from app.schemas import UploadInitRequest
            with pytest.raises(ValidationError):
                UploadInitRequest(filename="v.mp4", file_size_bytes=0, mime_type="video/mp4")
                class TestJobStageEnum:
                    def test_all_stages_valid(self):
                        from app.schemas import JobStage
                        stages = [
                        "pending", "uploading", "uploaded", "validating",
                        "extracting_frames", "detecting_faces", "running_inference",
                        "aggregating", "completed", "failed",
                ]
                for s in stages:
                    assert JobStage(s) is not None
                    def test_invalid_stage_raises(self):
                        from app.schemas import JobStage
                        with pytest.raises(ValueError):
                            JobStage("not_a_stage")
                            class TestWSEvent:
                                def test_serializes_to_json(self):
                                    from app.schemas import WSEvent, JobStage
                                    event = WSEvent(
                                    event="stage_change",
                                    job_id="abc-123",
                                    stage=JobStage.EXTRACTING_FRAMES,
                                    stage_progress=0.5,
                            )
                            data = event.model_dump_json()
                            assert "extracting_frames" in data
                            assert "abc-123" in data
                            def test_ts_is_set_automatically(self):
                                from app.schemas import WSEvent, JobStage
                                import time
                                before = time.time()
                                event = WSEvent(event="x", job_id="y", stage=JobStage.PENDING, stage_progress=0.0)
                                after = time.time()
                                assert before <= event.ts <= after
                                class TestVerdictEnum:
                                    def test_verdict_values(self):
                                        from app.schemas import Verdict
                                        assert Verdict.LIKELY_AI_GENERATED == "likely_ai_generated"
                                        assert Verdict.LIKELY_AUTHENTIC == "likely_authentic"
                                        assert Verdict.INCONCLUSIVE == "inconclusive"
