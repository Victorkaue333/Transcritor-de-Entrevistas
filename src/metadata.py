from datetime import datetime
from pathlib import Path


def build_metadata(input_file: str, model_name: str, language: str, segments: list) -> dict:
    file_path = Path(input_file)

    duration_seconds = 0
    if segments:
        duration_seconds = int(segments[-1]["end"])

    hours = duration_seconds // 3600
    minutes = (duration_seconds % 3600) // 60
    seconds = duration_seconds % 60

    readable_duration = f"{hours:02}:{minutes:02}:{seconds:02}"

    return {
        "interview_name": file_path.stem,
        "source_file": file_path.name,
        "language": language,
        "model": model_name,
        "processed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "duration": readable_duration,
        "total_segments": len(segments),
    }