import json
from pathlib import Path

CONFIG_MARKER = "hard-v3-config-path-16"

def load_mode():
    data = json.loads(Path("config/settings_alpha.json").read_text(encoding="utf-8"))
    return data["mode"]

def preserve_marker():
    return CONFIG_MARKER
