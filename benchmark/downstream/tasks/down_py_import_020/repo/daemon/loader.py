from pathlib import Path

def load_value():
    return Path("fixtures/input.txt").read_text(encoding="utf-8").strip()
