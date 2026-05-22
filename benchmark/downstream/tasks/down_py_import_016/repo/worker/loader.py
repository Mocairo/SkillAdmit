from pathlib import Path

def load_value():
    return Path("inputs/value.txt").read_text(encoding="utf-8").strip()
