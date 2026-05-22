import json
from pathlib import Path

CONFIG_MARKER = "hard-v4-workspace-config-14"

def load_region():
    data = json.loads(Path("config/runtime_beta.json").read_text(encoding="utf-8"))
    return data["region"]

def preserve_marker():
    return CONFIG_MARKER
