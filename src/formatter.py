from src.utils import seconds_to_readable_time, seconds_to_timestamp


def format_segments_to_txt(segments: list) -> str:
    """
    Formata os segmentos em texto legível com timestamps.
    """
    blocks = []

    for segment in segments:
        start = seconds_to_readable_time(segment["start"])
        end = seconds_to_readable_time(segment["end"])
        text = segment["text"].strip()

        block = f"[{start} --> {end}]\n{text}\n"
        blocks.append(block)

    return "\n".join(blocks)


def format_segments_to_json(segments: list) -> list:
    """
    Estrutura os segmentos em formato JSON serializável.
    """
    formatted = []

    for segment in segments:
        formatted.append({
            "start_seconds": round(segment["start"], 2),
            "end_seconds": round(segment["end"], 2),
            "start_time": seconds_to_readable_time(segment["start"]),
            "end_time": seconds_to_readable_time(segment["end"]),
            "text": segment["text"].strip()
        })

    return formatted


def format_segments_to_srt(segments: list) -> str:
    """
    Converte os segmentos em formato SRT.
    """
    srt_blocks = []

    for index, segment in enumerate(segments, start=1):
        start = seconds_to_timestamp(segment["start"])
        end = seconds_to_timestamp(segment["end"])
        text = segment["text"].strip()

        block = f"{index}\n{start} --> {end}\n{text}\n"
        srt_blocks.append(block)

    return "\n".join(srt_blocks)