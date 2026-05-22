from pathlib import Path

def load_value():
    return Path("resources/data.txt").read_text(encoding="utf-8").strip()
