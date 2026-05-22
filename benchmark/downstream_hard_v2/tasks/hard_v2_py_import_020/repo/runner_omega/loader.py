from pathlib import Path

LABEL = "cwd-hard-v2-20"

def load_value():
    return Path("data/omega.txt").read_text(encoding="utf-8").strip()

def preserve_label():
    return LABEL
