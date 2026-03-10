import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description="Transcrição automática de entrevistas com Whisper."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Caminho do arquivo de áudio ou vídeo."
    )

    parser.add_argument(
        "--model",
        default="medium",
        help="Modelo do Whisper: tiny, base, small, medium, large"
    )

    parser.add_argument(
        "--language",
        default="pt",
        help="Idioma da transcrição. Ex: pt, en, es"
    )

    parser.add_argument(
        "--output-name",
        default="transcript",
        help="Nome base dos arquivos de saída"
    )

    return parser.parse_args()