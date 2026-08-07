from typing import Any
class DeepfakeAPIError(Exception):
    status_code: int = 500
    code: str = "internal_error"
    def __init__(self, message: str, detail: Any = None) -> None:
        super().__init__(message)
        self.message = message
        self.detail = detail
    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "message": self.message,
            "detail": self.detail,
        }
class InvalidRequestError(DeepfakeAPIError):
    status_code = 400
    code = "invalid_request"
class InvalidFileError(DeepfakeAPIError):
    status_code = 422
    code = "invalid_file"
class FileTooLargeError(DeepfakeAPIError):
    status_code = 413
    code = "file_too_large"
class UnsupportedFormatError(DeepfakeAPIError):
    status_code = 415
    code = "unsupported_format"
class MissingChunkError(DeepfakeAPIError):
    status_code = 400
    code = "missing_chunk"
class JobNotFoundError(DeepfakeAPIError):
    status_code = 404
    code = "job_not_found"
    def __init__(self, job_id: str) -> None:
        super().__init__(f"Job '{job_id}' not found", detail={"job_id": job_id})
class ResultNotReadyError(DeepfakeAPIError):
    status_code = 404
    code = "result_not_ready"
    def __init__(self, job_id: str, stage: str) -> None:
        super().__init__(
            f"Result for job '{job_id}' is not ready yet (current stage: {stage})",
            detail={"job_id": job_id, "stage": stage},
        )
class JobAlreadyCompletedError(DeepfakeAPIError):
    status_code = 409
    code = "job_already_completed"
class PipelineError(DeepfakeAPIError):
    status_code = 500
    code = "pipeline_error"
class VideoValidationError(PipelineError):
    status_code = 422
    code = "video_validation_failed"
class ModelLoadError(PipelineError):
    status_code = 503
    code = "model_load_failed"
class FrameExtractionError(PipelineError):
    status_code = 500
    code = "frame_extraction_failed"
