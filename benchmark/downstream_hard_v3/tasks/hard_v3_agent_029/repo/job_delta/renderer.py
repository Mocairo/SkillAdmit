from pathlib import Path

TEMPLATE_MARKER = "hard-v3-template-path-29"

def render_report(name):
    template = Path("assets/templates/summary_delta.txt").read_text(encoding="utf-8").strip()
    return template.replace("{name}", name)

def preserve_marker():
    return TEMPLATE_MARKER
