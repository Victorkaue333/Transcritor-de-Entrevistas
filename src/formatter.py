from src.utils import seconds_to_readable_time, seconds_to_timestamp


def format_metadata_header(metadata: dict) -> str:
    return (
        f"Entrevista: {metadata['interview_name']}\n"
        f"Arquivo: {metadata['source_file']}\n"
        f"Duração: {metadata['duration']}\n"
        f"Idioma: {metadata['language']}\n"
        f"Modelo Whisper: {metadata['model']}\n"
        f"Data de processamento: {metadata['processed_at']}\n"
        f"Total de segmentos: {metadata['total_segments']}\n"
    )


def format_segments_to_txt(segments: list, metadata: dict) -> str:
    blocks = [format_metadata_header(metadata), "-" * 60, ""]

    for segment in segments:
        start = seconds_to_readable_time(segment["start"])
        end = seconds_to_readable_time(segment["end"])
        text = segment["text"].strip()

        block = f"[{start} --> {end}]\n{text}\n"
        blocks.append(block)

    return "\n".join(blocks)


def format_segments_to_json(segments: list, metadata: dict) -> dict:
    return {
        "metadata": metadata,
        "segments": [
            {
                "start_seconds": round(segment["start"], 2),
                "end_seconds": round(segment["end"], 2),
                "start_time": seconds_to_readable_time(segment["start"]),
                "end_time": seconds_to_readable_time(segment["end"]),
                "text": segment["text"].strip(),
            }
            for segment in segments
        ]
    }


def format_segments_to_srt(segments: list) -> str:
    srt_blocks = []

    for index, segment in enumerate(segments, start=1):
        start = seconds_to_timestamp(segment["start"])
        end = seconds_to_timestamp(segment["end"])
        text = segment["text"].strip()

        srt_blocks.append(f"{index}\n{start} --> {end}\n{text}\n")

    return "\n".join(srt_blocks)