from pathlib import Path

TEMPLATE_MARKER = "hard-v4-resource-template-18"

def render_notice(name):
    template = Path("resources/templates/notice_beta.txt").read_text(encoding="utf-8").strip()
    return template.replace("{name}", name)

def preserve_marker():
    return TEMPLATE_MARKER
