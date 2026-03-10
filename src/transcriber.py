import whisper
from src.config import WHISPER_MODEL, LANGUAGE


def transcribe_file(file_path: str) -> dict:
    """
    Transcreve um arquivo de áudio/vídeo com Whisper.
    Retorna o resultado completo com segmentos.
    """
    model = whisper.load_model(WHISPER_MODEL)

    result = model.transcribe(
        str(file_path),
        language=LANGUAGE,
        verbose=True
    )

    return result