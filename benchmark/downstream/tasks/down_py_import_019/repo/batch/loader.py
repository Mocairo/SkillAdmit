from pathlib import Path

def load_value():
    return Path("payloads/message.txt").read_text(encoding="utf-8").strip()
