from pathlib import Path

LABEL = "cwd-hard-v2-19"

def load_value():
    return Path("data/delta.txt").read_text(encoding="utf-8").strip()

def preserve_label():
    return LABEL
