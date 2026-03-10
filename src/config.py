from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"

INPUT_FILE = INPUT_DIR / "entrevista.mp4"

OUTPUT_TXT = OUTPUT_DIR / "transcript.txt"
OUTPUT_JSON = OUTPUT_DIR / "transcript.json"
OUTPUT_SRT = OUTPUT_DIR / "transcript.srt"

WHISPER_MODEL = "medium"
LANGUAGE = "pt"