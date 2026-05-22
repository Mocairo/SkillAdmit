from pathlib import Path

LABEL = "cwd-hard-v1"

def load_value():
    return Path("data/value.txt").read_text(encoding="utf-8").strip()

def preserve_label():
    return LABEL
