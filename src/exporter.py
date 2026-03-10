import json
from pathlib import Path


def ensure_output_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def save_txt(content: str, output_path: Path) -> None:
    ensure_output_dir(output_path)

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(content)


def save_json(content: list, output_path: Path) -> None:
    ensure_output_dir(output_path)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(content, file, ensure_ascii=False, indent=2)


def save_srt(content: str, output_path: Path) -> None:
    ensure_output_dir(output_path)

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(content)