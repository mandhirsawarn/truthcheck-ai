# API Documentation

TruthCheck AI exposes a RESTful API powered by FastAPI.

## Base URL
`/api/v1`

## Endpoints

### Uploads
- `POST /uploads/init` - Initializes a chunked media upload session.
- `PUT /uploads/{job_id}/chunk` - Uploads a specific chunk of the media.
- `POST /uploads/{job_id}/complete` - Finalizes the upload and dispatches the AI pipeline.

### Jobs & Polling
- `GET /jobs` - Returns a paginated list of all active and completed jobs.
- `GET /jobs/{job_id}` - Returns the current processing status and progress of a specific job.

### Results & Investigations
- `GET /results/{job_id}` - Retrieves the full forensic result, including the verdict and multi-stream confidence scores.
- `GET /results/{job_id}/frames` - Retrieves paginated granular scores for individual frames within the media.
- `PATCH /results/{job_id}/investigation` - Updates the investigation status and investigator notes.
- `GET /results/{job_id}/export` - Generates and returns a downloadable JSON/CSV artifact for the forensic case.

## Authentication
*(Currently disabled in local development)*. In production, endpoints are secured via JWT Bearer tokens.
