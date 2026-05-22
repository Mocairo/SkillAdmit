import json
from pathlib import Path

CONFIG_MARKER = "hard-v3-config-path-20"

def load_mode():
    data = json.loads(Path("config/settings_omega.json").read_text(encoding="utf-8"))
    return data["mode"]

def preserve_marker():
    return CONFIG_MARKER
