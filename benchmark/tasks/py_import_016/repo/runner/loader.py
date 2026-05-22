from pathlib import Path

def load_value():
    return Path("resources/input.txt").read_text(encoding="utf-8").strip()
