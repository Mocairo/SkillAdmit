from pathlib import Path

LABEL = "cwd-hard-v2-18"

def load_value():
    return Path("data/gamma.txt").read_text(encoding="utf-8").strip()

def preserve_label():
    return LABEL
