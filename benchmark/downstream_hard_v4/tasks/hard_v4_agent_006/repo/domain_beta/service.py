from formatters import format_slug

SERVICE_MARKER = "hard-v4-src-layout-6"

def build_slug(value):
    return format_slug(value)

def preserve_marker():
    return SERVICE_MARKER
