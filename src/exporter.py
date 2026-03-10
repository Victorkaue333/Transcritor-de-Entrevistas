import json
from pathlib import Path


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def save_txt(content: str, output_path: Path, logger=None) -> None:
    ensure_parent_dir(output_path)
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(content)

    if logger:
        logger.info("Arquivo TXT salvo em: %s", output_path)


def save_json(content: dict, output_path: Path, logger=None) -> None:
    ensure_parent_dir(output_path)
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(content, file, ensure_ascii=False, indent=2)

    if logger:
        logger.info("Arquivo JSON salvo em: %s", output_path)


def save_srt(content: str, output_path: Path, logger=None) -> None:
    ensure_parent_dir(output_path)
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(content)

    if logger:
        logger.info("Arquivo SRT salvo em: %s", output_path)