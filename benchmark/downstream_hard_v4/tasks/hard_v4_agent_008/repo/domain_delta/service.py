from labels import label_slug

SERVICE_MARKER = "hard-v4-src-layout-8"

def build_slug(value):
    return label_slug(value)

def preserve_marker():
    return SERVICE_MARKER
