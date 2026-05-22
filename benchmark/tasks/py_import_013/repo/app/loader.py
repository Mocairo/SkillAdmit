from pathlib import Path

def load_value():
    return Path("data/config.txt").read_text(encoding="utf-8").strip()
