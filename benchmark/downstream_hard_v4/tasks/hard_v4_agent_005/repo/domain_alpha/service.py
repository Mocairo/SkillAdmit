from normalizers import normalize_slug

SERVICE_MARKER = "hard-v4-src-layout-5"

def build_slug(value):
    return normalize_slug(value)

def preserve_marker():
    return SERVICE_MARKER
