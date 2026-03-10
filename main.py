from pathlib import Path
import sys

from src.cli import parse_args
from src.cleaner import clean_segments
from src.config import LOG_DIR, OUTPUT_DIR
from src.exporter import save_json, save_srt, save_txt
from src.formatter import (
    format_segments_to_json,
    format_segments_to_srt,
    format_segments_to_txt,
)
from src.logger import setup_logger
from src.metadata import build_metadata
from src.transcriber import transcribe_file


def main():
    args = parse_args()
    logger = setup_logger(LOG_DIR)

    try:
        input_file = Path(args.input)

        if not input_file.exists():
            logger.error("Arquivo não encontrado: %s", input_file)
            raise FileNotFoundError(f"Arquivo não encontrado: {input_file}")

        logger.info("Execução iniciada")
        logger.info("Arquivo de entrada: %s", input_file)
        logger.info("Modelo: %s | Idioma: %s", args.model, args.language)

        result = transcribe_file(
            file_path=str(input_file),
            model_name=args.model,
            language=args.language,
            logger=logger,
        )

        raw_segments = result.get("segments", [])
        if not raw_segments:
            logger.error("Nenhum segmento foi retornado pela transcrição.")
            raise ValueError("Nenhum segmento foi retornado pela transcrição.")

        cleaned_segments = clean_segments(raw_segments)
        metadata = build_metadata(
            input_file=str(input_file),
            model_name=args.model,
            language=args.language,
            segments=cleaned_segments,
        )

        output_txt = OUTPUT_DIR / f"{args.output_name}.txt"
        output_json = OUTPUT_DIR / f"{args.output_name}.json"
        output_srt = OUTPUT_DIR / f"{args.output_name}.srt"

        txt_content = format_segments_to_txt(cleaned_segments, metadata)
        json_content = format_segments_to_json(cleaned_segments, metadata)
        srt_content = format_segments_to_srt(cleaned_segments)

        save_txt(txt_content, output_txt, logger=logger)
        save_json(json_content, output_json, logger=logger)
        save_srt(srt_content, output_srt, logger=logger)

        logger.info("Processamento finalizado com sucesso.")

    except Exception as exc:
        logger.exception("Erro durante a execução: %s", exc)
        sys.exit(1)
        
def run_cli():
    print("Modo CLI ainda ativo.")
    # aqui continua sua lógica atual de terminal

def run_web():
    import uvicorn
    uvicorn.run("src.api:app", host="127.0.0.1", port=8000, reload=True)

    if __name__ == "__main__":
        if len(sys.argv) > 1 and sys.argv[1] == "web":
            run_web()
        else:
            run_cli()