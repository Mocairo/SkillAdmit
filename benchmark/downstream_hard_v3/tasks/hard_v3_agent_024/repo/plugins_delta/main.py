from extensions.loader import load_plugin

PLUGIN_MARKER = "hard-v3-plugin-import-24"

def resolve():
    return load_plugin("delta")

def preserve_marker():
    return PLUGIN_MARKER
