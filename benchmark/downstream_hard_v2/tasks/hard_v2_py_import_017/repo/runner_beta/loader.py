from pathlib import Path

LABEL = "cwd-hard-v2-17"

def load_value():
    return Path("data/beta.txt").read_text(encoding="utf-8").strip()

def preserve_label():
    return LABEL
