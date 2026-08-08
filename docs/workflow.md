# Investigation Workflow

The TruthCheck AI workflow is designed to closely mirror professional digital forensics procedures while heavily integrating AI-driven insights to speed up case triage.

## 1. Evidence Submission
- **Upload**: An investigator or automated system submits a video file for analysis. Large files are handled via chunked uploads to ensure stability over poor network conditions.
- **Queueing**: The backend registers a new `Job` and sets the stage to `processing`.

## 2. AI Forensic Processing
Once the file is received, the AI pipeline executes:
1. **Frame Extraction**: The video is broken down into constituent frames.
2. **Face Detection**: Core subjects in the video are identified and bounded.
3. **Multi-Stream Scoring**: 
   - Each frame is scored across Spatial, Temporal, Frequency, and Compression matrices.
4. **Fusion**: A final confidence score and qualitative verdict (`likely_ai_generated`, `likely_authentic`, or `inconclusive`) are calculated.

## 3. Review & Triage
- **Dashboard Overview**: The investigator opens the TruthCheck dashboard, which immediately highlights evidence categorized by risk.
- **Detailed Investigation**: Clicking a case reveals the multi-stream breakdown, frame timeline, and metadata.
- **Manual Override & Noting**: The investigator can update the case status (e.g., from `Needs Review` to `Suspected`) and add specific context or notes based on the AI’s findings.

## 4. Reporting
- **Data Export**: The final verdict, accompanied by the AI's explanation bullets and timeline scores, can be downloaded as a CSV (for data teams) or a PDF (for legal/chain-of-custody documentation).
