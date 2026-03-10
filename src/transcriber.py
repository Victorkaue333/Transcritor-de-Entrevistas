import whisper


def transcribe_file(file_path: str, model_name: str, language: str, logger):
    logger.info("Carregando modelo Whisper: %s", model_name)
    model = whisper.load_model(model_name)

    logger.info("Iniciando transcrição do arquivo: %s", file_path)
    result = model.transcribe(
        file_path,
        language=language,
        verbose=False
    )

    logger.info("Transcrição concluída com sucesso.")
    return result