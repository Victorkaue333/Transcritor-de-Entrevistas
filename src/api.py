from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.services.transcript_service import TranscriptService

BASE_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(title="Whisper Interview Transcriber")

service = TranscriptService()

# arquivos estáticos do frontend
app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")


@app.get("/")
def read_index():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.post("/api/upload")
async def upload_video(
    file: UploadFile = File(...),
    enable_diarization: bool = Form(False)
):
    allowed_extensions = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".mp3", ".wav", ".m4a"}
    suffix = Path(file.filename).suffix.lower()

    if suffix not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Formato não suportado. Envie vídeo ou áudio válido.",
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_path = Path(temp_file.name)

    try:
        result = service.process_video(temp_path, file.filename, enable_diarization)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {exc}") from exc
    finally:
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)


@app.get("/api/transcript/{job_id}")
def get_transcript(job_id: str):
    data = service.get_transcript(job_id)
    if not data:
        raise HTTPException(status_code=404, detail="Transcrição não encontrada.")
    return data


@app.get("/api/download/{job_id}/{format}")
def download_transcript(job_id: str, format: str):
    """Download da transcrição em TXT, JSON ou SRT"""
    if format not in ["txt", "json", "srt"]:
        raise HTTPException(status_code=400, detail="Formato inválido. Use txt, json ou srt.")
    
    file_path = service.get_download_file(job_id, format)
    if not file_path or not file_path.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.")
    
    return FileResponse(
        path=file_path,
        filename=f"{job_id}.{format}",
        media_type="application/octet-stream"
    )