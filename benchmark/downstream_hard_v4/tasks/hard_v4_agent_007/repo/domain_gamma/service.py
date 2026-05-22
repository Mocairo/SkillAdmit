from presenters import present_slug

SERVICE_MARKER = "hard-v4-src-layout-7"

def build_slug(value):
    return present_slug(value)

def preserve_marker():
    return SERVICE_MARKER
