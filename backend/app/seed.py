import uuid
import random
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Job, AnalysisResult
from app.schemas import JobStage

def _now() -> datetime:
    return datetime.now(timezone.utc)

async def seed_if_empty(session: AsyncSession):
    count = await session.scalar(select(func.count()).select_from(Job))
    if count > 0:
        return

    print("Seeding database with demo records...")
    
    # 3 Verified, 3 Suspected, 2 Needs Review
    templates = [
        # Verified
        {"status": "Verified", "verdict": "likely_authentic", "conf": 8.5, "notes": "No synthetic artifacts detected. Lighting is consistent.", "name": "interview_clip_4.mp4"},
        {"status": "Verified", "verdict": "likely_authentic", "conf": 4.2, "notes": "Verified by secondary source. Authentic footage.", "name": "street_cam_02.mp4"},
        {"status": "Verified", "verdict": "likely_authentic", "conf": 12.0, "notes": "Natural skin texture and blinking rate.", "name": "press_conference.mp4"},
        
        # Suspected
        {"status": "Suspected", "verdict": "likely_ai_generated", "conf": 98.4, "notes": "Clear GAN artifacts around the mouth. Unnatural blinking.", "name": "ceo_statement_leaked.mp4"},
        {"status": "Suspected", "verdict": "likely_ai_generated", "conf": 95.1, "notes": "Inconsistent lighting on face vs background. Audio desync.", "name": "viral_news_clip.mp4"},
        {"status": "Suspected", "verdict": "likely_ai_generated", "conf": 89.7, "notes": "Deepfake detected by spatial and temporal streams.", "name": "political_ad.mp4"},
        
        # Needs Review
        {"status": "Needs Review", "verdict": "inconclusive", "conf": 45.2, "notes": "Low resolution footage makes it hard to confirm. Manual review needed.", "name": "cctv_footage_night.mp4"},
        {"status": "Needs Review", "verdict": "likely_ai_generated", "conf": 62.8, "notes": "Borderline score. Needs expert human analysis on audio.", "name": "zoom_call_recording.mp4"},
    ]
    
    for i, t in enumerate(templates):
        job_id = str(uuid.uuid4())
        created = _now() - timedelta(hours=i*3)
        
        is_ai = t["verdict"] == "likely_ai_generated"
        spatial = random.uniform(80, 99) if is_ai else random.uniform(2, 20)
        freq = random.uniform(80, 99) if is_ai else random.uniform(2, 20)
        temp = random.uniform(80, 99) if is_ai else random.uniform(2, 20)
        comp = random.uniform(80, 99) if is_ai else random.uniform(2, 20)
        
        if t["verdict"] == "inconclusive":
            spatial, freq, temp, comp = [random.uniform(30, 60) for _ in range(4)]
            
        job = Job(
            id=job_id,
            filename=t["name"],
            original_filename=t["name"],
            file_path=None,
            file_size_bytes=random.randint(1000000, 50000000),
            mime_type="video/mp4",
            total_chunks=1,
            chunks_received=1,
            stage=JobStage.COMPLETED,
            stage_progress=1.0,
            created_at=created,
            investigation_status=t["status"],
            investigation_notes=t["notes"]
        )
        
        bullets = []
        if is_ai:
            bullets = ["Detected spatial inconsistencies", "Temporal flicker detected", "Frequency spectrum anomalies"]
        elif t["verdict"] == "likely_authentic":
            bullets = ["Natural noise distribution", "Consistent facial lighting", "Normal compression patterns"]
        else:
            bullets = ["Mixed signals", "Low confidence across all streams", "Requires manual review"]
            
        result = AnalysisResult(
            job_id=job_id,
            verdict=t["verdict"],
            confidence=t["conf"],
            spatial_confidence=spatial,
            frequency_confidence=freq,
            temporal_confidence=temp,
            compression_confidence=comp,
            model_version="demo-1.0",
            processing_time_ms=random.randint(1500, 8000),
            frames_analyzed=random.randint(30, 150),
            faces_detected_in=random.randint(20, 140),
            video_duration_seconds=random.uniform(5.0, 60.0),
            video_fps=30.0,
            video_width=1920,
            video_height=1080,
            video_codec="h264",
            explanation_bullets=bullets,
            evidence_frame_urls=["/media/placeholder.jpg"],
            created_at=created
        )
        
        session.add(job)
        session.add(result)
        
    await session.commit()
    print("Demo dataset seeded successfully.")
