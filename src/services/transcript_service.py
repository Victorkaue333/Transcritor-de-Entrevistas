from __future__ import annotations

import json
import shutil
import uuid
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[2]
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
FRONTEND_MEDIA_DIR = BASE_DIR / "frontend" / "media"

INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
FRONTEND_MEDIA_DIR.mkdir(parents=True, exist_ok=True)


class TranscriptService:
    def __init__(self) -> None:
        self.input_dir = INPUT_DIR
        self.output_dir = OUTPUT_DIR
        self.frontend_media_dir = FRONTEND_MEDIA_DIR

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

    def process_video(self, source_file_path: Path, original_filename: str) -> dict[str, Any]:
        saved = self.save_upload(source_file_path, original_filename)

        raw_result = self._run_existing_transcriber(saved["input_path"], saved["job_id"])
        normalized_segments = self._normalize_segments(raw_result)

        result_payload = {
            "job_id": saved["job_id"],
            "video_url": saved["media_url"],
            "segments": normalized_segments,
        }

        output_json = self.output_dir / f"{saved['job_id']}_segments.json"
        with output_json.open("w", encoding="utf-8") as f:
            json.dump(result_payload, f, ensure_ascii=False, indent=2)

        return result_payload

    def get_transcript(self, job_id: str) -> dict[str, Any] | None:
        transcript_path = self.output_dir / f"{job_id}_segments.json"
        if not transcript_path.exists():
            return None

        with transcript_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _run_existing_transcriber(self, input_video_path: Path, job_id: str) -> Any:
        """
        ADAPTE AQUI para encaixar no seu transcriber.py atual.

        Opção A:
            Se seu transcriber já retorna algo como:
            {
              "segments": [{"start": ..., "end": ..., "text": ...}]
            }
            basta retornar esse objeto.

        Opção B:
            Se ele salva um JSON em output/, você pode carregar esse JSON aqui.

        Opção C:
            Se ele expõe uma função tipo transcribe_file(path), use ela aqui.
        """
        # ===== EXEMPLO DE INTEGRAÇÃO =====
        #
        # from src.transcriber import transcribe_file
        # result = transcribe_file(str(input_video_path))
        # return result
        #
        # ===== EXEMPLO 2: lendo um arquivo já gerado =====
        #
        # generated_json = self.output_dir / f"{job_id}_raw.json"
        # with generated_json.open("r", encoding="utf-8") as f:
        #     return json.load(f)

        # ===== FALLBACK TEMPORÁRIO PARA TESTAR A UI =====
        return {
            "segments": [
                {
                    "start": 0.0,
                    "end": 5.0,
                    "speaker": "Desconhecido",
                    "text": "Teste inicial da interface de transcrição.",
                },
                {
                    "start": 5.0,
                    "end": 11.0,
                    "speaker": "Desconhecido",
                    "text": "Quando você conectar o transcriber real, os trechos vão aparecer aqui.",
                },
            ]
        }

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