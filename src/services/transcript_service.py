from __future__ import annotations

import json
import shutil
import uuid
from pathlib import Path
from typing import Any

from src.logger import setup_logger
from src.transcriber import transcribe_file

BASE_DIR = Path(__file__).resolve().parents[2]
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
FRONTEND_MEDIA_DIR = BASE_DIR / "frontend" / "media"
LOG_DIR = BASE_DIR / "logs"

INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
FRONTEND_MEDIA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)


class TranscriptService:
    def __init__(self) -> None:
        self.input_dir = INPUT_DIR
        self.output_dir = OUTPUT_DIR
        self.frontend_media_dir = FRONTEND_MEDIA_DIR
        self.logger = setup_logger(LOG_DIR)

    def save_upload(self, source_file_path: Path, original_filename: str) -> dict[str, Any]:
        job_id = str(uuid.uuid4())[:8]

        safe_name = original_filename.replace(" ", "_")
        input_filename = f"{job_id}_{safe_name}"
        input_path = self.input_dir / input_filename

        shutil.copy2(source_file_path, input_path)

        # cópia para o frontend tocar no player
        media_filename = input_filename
        media_path = self.frontend_media_dir / media_filename
        shutil.copy2(input_path, media_path)

        return {
            "job_id": job_id,
            "input_path": input_path,
            "media_filename": media_filename,
            "media_url": f"/frontend/media/{media_filename}",
        }

    def process_video(self, source_file_path: Path, original_filename: str, enable_diarization: bool = False) -> dict[str, Any]:
        saved = self.save_upload(source_file_path, original_filename)

        raw_result = self._run_existing_transcriber(saved["input_path"], saved["job_id"])
        
        # Se diarization estiver habilitado, aplica identificação de speakers
        if enable_diarization:
            try:
                self.logger.info(f"Aplicando diarization para job_id: {saved['job_id']}")
                raw_result = self._apply_diarization(saved["input_path"], raw_result)
            except Exception as e:
                self.logger.warning(f"Falha ao aplicar diarization: {e}. Continuando sem identificação de speakers.")
        
        normalized_segments = self._normalize_segments(raw_result)

        result_payload = {
            "job_id": saved["job_id"],
            "video_url": saved["media_url"],
            "segments": normalized_segments,
        }

        # Salva JSON
        output_json = self.output_dir / f"{saved['job_id']}_segments.json"
        with output_json.open("w", encoding="utf-8") as f:
            json.dump(result_payload, f, ensure_ascii=False, indent=2)

        # Gera arquivos TXT e SRT para download
        self._generate_download_files(saved["job_id"], normalized_segments)

        return result_payload

    def get_transcript(self, job_id: str) -> dict[str, Any] | None:
        transcript_path = self.output_dir / f"{job_id}_segments.json"
        if not transcript_path.exists():
            return None

        with transcript_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _run_existing_transcriber(self, input_video_path: Path, job_id: str) -> Any:
        """
        Executa o transcriber do Whisper no arquivo de vídeo/áudio.
        Retorna o resultado com os segmentos transcritos.
        """
        try:
            self.logger.info(f"Iniciando transcrição para job_id: {job_id}")
            
            # Usando modelo base e detecção automática de idioma
            # Você pode alterar para "small", "medium", "large" conforme necessário
            result = transcribe_file(
                file_path=str(input_video_path),
                model_name="base",
                language="pt",
                logger=self.logger
            )
            
            self.logger.info(f"Transcrição concluída para job_id: {job_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Erro ao transcrever arquivo {input_video_path}: {e}")
            raise

    def _apply_diarization(self, audio_path: Path, whisper_result: Any) -> Any:
        """
        Aplica speaker diarization usando pyannote.audio.
        Requer: pip install pyannote.audio
        E um token do HuggingFace com aceite dos termos em:
        https://huggingface.co/pyannote/speaker-diarization-3.1
        """
        try:
            from pyannote.audio import Pipeline
            import torch
            
            # Carrega o pipeline de diarization
            # NOTA: Na primeira vez, você precisa aceitar os termos em huggingface.co
            # e usar seu token: Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token="YOUR_TOKEN")
            pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=True  # Usa o token do HF_TOKEN environment variable
            )
            
            # Aplica diarization
            diarization = pipeline(str(audio_path))
            
            # Mapeia speakers para os segmentos do Whisper
            segments = whisper_result.get("segments", [])
            
            for segment in segments:
                start_time = segment.get("start", 0.0)
                end_time = segment.get("end", 0.0)
                mid_time = (start_time + end_time) / 2
                
                # Encontra o speaker no tempo médio do segmento
                speaker_label = None
                for turn, _, speaker in diarization.itertracks(yield_label=True):
                    if turn.start <= mid_time <= turn.end:
                        speaker_label = speaker
                        break
                
                segment["speaker"] = speaker_label if speaker_label else "Desconhecido"
            
            whisper_result["segments"] = segments
            return whisper_result
            
        except ImportError:
            self.logger.warning("pyannote.audio não instalado. Execute: pip install pyannote.audio")
            return whisper_result
        except Exception as e:
            self.logger.error(f"Erro ao aplicar diarization: {e}")
            return whisper_result

    def _generate_download_files(self, job_id: str, segments: list[dict[str, Any]]) -> None:
        """Gera arquivos TXT e SRT para download"""
        try:
            # Gera TXT simples
            txt_lines = []
            for segment in segments:
                start = self._seconds_to_time(segment["start"])
                end = self._seconds_to_time(segment["end"])
                speaker = segment.get("speaker", "Desconhecido")
                text = segment.get("text", "").strip()
                
                txt_lines.append(f"[{start} --> {end}] {speaker}")
                txt_lines.append(text)
                txt_lines.append("")
            
            txt_content = "\n".join(txt_lines)
            txt_path = self.output_dir / f"{job_id}.txt"
            with txt_path.open("w", encoding="utf-8") as f:
                f.write(txt_content)
            
            # Gera SRT
            srt_lines = []
            for index, segment in enumerate(segments, start=1):
                start = self._seconds_to_srt_time(segment["start"])
                end = self._seconds_to_srt_time(segment["end"])
                text = segment.get("text", "").strip()
                
                srt_lines.append(str(index))
                srt_lines.append(f"{start} --> {end}")
                srt_lines.append(text)
                srt_lines.append("")
            
            srt_content = "\n".join(srt_lines)
            srt_path = self.output_dir / f"{job_id}.srt"
            with srt_path.open("w", encoding="utf-8") as f:
                f.write(srt_content)
            
            self.logger.info(f"Arquivos de download gerados para job_id: {job_id}")
        except Exception as e:
            self.logger.error(f"Erro ao gerar arquivos de download: {e}")

    def _seconds_to_time(self, seconds: float) -> str:
        """Converte segundos para formato HH:MM:SS"""
        total = int(seconds)
        hrs = total // 3600
        mins = (total % 3600) // 60
        secs = total % 60
        
        if hrs > 0:
            return f"{hrs:02d}:{mins:02d}:{secs:02d}"
        return f"{mins:02d}:{secs:02d}"
    
    def _seconds_to_srt_time(self, seconds: float) -> str:
        """Converte segundos para formato SRT (HH:MM:SS,mmm)"""
        total = int(seconds)
        millis = int((seconds - total) * 1000)
        hrs = total // 3600
        mins = (total % 3600) // 60
        secs = total % 60
        
        return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

    def get_download_file(self, job_id: str, format: str) -> Path | None:
        """Retorna o caminho do arquivo de download no formato especificado"""
        if format == "json":
            file_path = self.output_dir / f"{job_id}_segments.json"
        else:
            file_path = self.output_dir / f"{job_id}.{format}"
        
        return file_path if file_path.exists() else None

    def _normalize_segments(self, raw_result: Any) -> list[dict[str, Any]]:
        """
        Normaliza a saída para o formato:
        [
          {
            "start": 31.0,
            "end": 39.0,
            "speaker": "Desconhecido",
            "text": "..."
          }
        ]
        """
        if isinstance(raw_result, dict) and "segments" in raw_result:
            segments = raw_result["segments"]
        elif isinstance(raw_result, list):
            segments = raw_result
        else:
            raise ValueError("Formato de transcrição não suportado.")

        normalized: list[dict[str, Any]] = []

        for item in segments:
            normalized.append(
                {
                    "start": float(item.get("start", 0.0)),
                    "end": float(item.get("end", 0.0)),
                    "speaker": item.get("speaker", "Desconhecido"),
                    "text": str(item.get("text", "")).strip(),
                }
            )

        return normalized