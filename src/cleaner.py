import re


def clean_text_block(text: str) -> str:
    """
    Limpeza simples do texto para melhorar legibilidade.
    """
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\b(ééé|eh eh|hum hum)\b", "", text, flags=re.IGNORECASE)
    return text


def clean_segments(segments: list) -> list:
    cleaned = []

    for segment in segments:
        cleaned.append({
            **segment,
            "text": clean_text_block(segment["text"])
        })

    return cleaned