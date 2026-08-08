# Database Schema

TruthCheck AI utilizes SQLite with SQLAlchemy ORM for fast, localized, and file-based data persistence. The schema is optimized for write-heavy AI pipelines and read-heavy dashboard analytics.

## Tables

### 1. `jobs`
Tracks the lifecycle of an uploaded piece of evidence.
- `id` (String): UUID primary key.
- `filename`, `original_filename` (Text): Media identifiers.
- `stage` (String): Current processing state (`pending`, `processing`, `completed`, `failed`).
- `investigation_status` (String): Case state set by investigators (`Verified`, `Suspected`, `Needs Review`).
- `investigation_notes` (Text): Manual annotations.
- `created_at`, `updated_at` (DateTime): Auditing timestamps.

### 2. `analysis_results`
Stores the aggregated outcome of the AI detection pipeline.
- `id` (String): UUID primary key.
- `job_id` (String): Foreign key to `jobs`.
- `verdict` (String): Final AI decision.
- `confidence` (Float): Overall fusion probability score (0-100%).
- `spatial_confidence`, `temporal_confidence`, `frequency_confidence`, `compression_confidence` (Float): Granular subsystem scores.
- `explanation_bullets` (JSON): Automatically generated insights explaining the verdict.

### 3. `frame_scores`
Stores granular, per-frame tracking data for timeline visualization.
- `id` (Integer): Primary key.
- `result_id` (String): Foreign key to `analysis_results`.
- `frame_index` (Integer): Sequential frame number.
- `timestamp_seconds` (Float): Temporal location in the video.
- `fusion_score` (Float): Confidence score specific to this frame.
- `has_face` (Boolean): Indicates whether a face bounding box was tracked.
