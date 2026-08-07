import asyncio
import shutil
from pathlib import Path
import aiofiles
import aiofiles.os
from app.config import settings
def job_dir(job_id: str) -> Path:
    return settings.UPLOAD_DIR / job_id
def chunks_dir(job_id: str) -> Path:
    d = job_dir(job_id) / "chunks"
    d.mkdir(parents=True, exist_ok=True)
    return d
def frames_dir(job_id: str) -> Path:
    d = job_dir(job_id) / "frames"
    d.mkdir(parents=True, exist_ok=True)
    return d
def audio_dir(job_id: str) -> Path:
    d = job_dir(job_id) / "audio"
    d.mkdir(parents=True, exist_ok=True)
    return d
def source_video_path(job_id: str, extension: str = ".mp4") -> Path:
    job_dir(job_id).mkdir(parents=True, exist_ok=True)
    return job_dir(job_id) / f"source{extension}"
def thumb_path(job_id: str) -> Path:
    return job_dir(job_id) / "thumb.jpg"
def frame_url(job_id: str, frame_filename: str) -> str:
    return f"{settings.PUBLIC_BASE_URL}/media/{job_id}/frames/{frame_filename}"
def thumb_url(job_id: str) -> str:
    return f"{settings.PUBLIC_BASE_URL}/media/{job_id}/thumb.jpg"
async def save_chunk(job_id: str, chunk_index: int, data: bytes) -> Path:
    chunk_path = chunks_dir(job_id) / f"chunk_{chunk_index:06d}.part"
    async with aiofiles.open(chunk_path, "wb") as f:
        await f.write(data)
    return chunk_path
async def assemble_chunks(job_id: str, total_chunks: int, extension: str = ".mp4") -> Path:
    dest = source_video_path(job_id, extension)
    c_dir = chunks_dir(job_id)
    async with aiofiles.open(dest, "wb") as out_f:
        for i in range(total_chunks):
            chunk_path = c_dir / f"chunk_{i:06d}.part"
            if not chunk_path.exists():
                raise FileNotFoundError(
                    f"Missing chunk {i} of {total_chunks} for job {job_id}"
                )
            async with aiofiles.open(chunk_path, "rb") as in_f:
                while True:
                    buf = await in_f.read(4 * 1024 * 1024)
                    if not buf:
                        break
                    await out_f.write(buf)
    await aiofiles.os.wrap(shutil.rmtree)(str(c_dir), ignore_errors=True)
    return dest
async def save_single_upload(job_id: str, data: bytes, extension: str = ".mp4") -> Path:
    dest = source_video_path(job_id, extension)
    job_dir(job_id).mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(dest, "wb") as f:
        await f.write(data)
    return dest
async def cleanup_job(job_id: str) -> None:
    d = job_dir(job_id)
    if d.exists():
        await aiofiles.os.wrap(shutil.rmtree)(str(d), ignore_errors=True)
async def cleanup_source_and_frames(job_id: str) -> None:
    for subdir in ("frames", "audio", "chunks"):
        d = job_dir(job_id) / subdir
        if d.exists():
            await aiofiles.os.wrap(shutil.rmtree)(str(d), ignore_errors=True)
    src = job_dir(job_id) / "source.mp4"
    if src.exists():
        await aiofiles.os.remove(str(src))
