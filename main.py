from pathlib import Path

from src.config import INPUT_FILE, OUTPUT_JSON, OUTPUT_SRT, OUTPUT_TXT
from src.transcriber import transcribe_file
from src.formatter import (
    format_segments_to_json,
    format_segments_to_srt,
    format_segments_to_txt,
)
from src.exporter import save_json, save_srt, save_txt


def validate_input_file(file_path: Path) -> None:
    if not file_path.exists():
        raise FileNotFoundError(
            f"Arquivo de entrada não encontrado: {file_path}"
        )


def main() -> None:
    print("Iniciando transcrição...")
    validate_input_file(INPUT_FILE)

    result = transcribe_file(INPUT_FILE)
    segments = result.get("segments", [])

    if not segments:
        raise ValueError("Nenhum segmento foi retornado pela transcrição.")

    txt_content = format_segments_to_txt(segments)
    json_content = format_segments_to_json(segments)
    srt_content = format_segments_to_srt(segments)

    save_txt(txt_content, OUTPUT_TXT)
    save_json(json_content, OUTPUT_JSON)
    save_srt(srt_content, OUTPUT_SRT)

    print("Transcrição finalizada com sucesso.")
    print(f"TXT salvo em: {OUTPUT_TXT}")
    print(f"JSON salvo em: {OUTPUT_JSON}")
    print(f"SRT salvo em: {OUTPUT_SRT}")


if __name__ == "__main__":
    main()