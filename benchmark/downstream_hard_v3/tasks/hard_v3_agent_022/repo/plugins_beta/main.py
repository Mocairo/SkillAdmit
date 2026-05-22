from catalog.loader import load_plugin

PLUGIN_MARKER = "hard-v3-plugin-import-22"

def resolve():
    return load_plugin("beta")

def preserve_marker():
    return PLUGIN_MARKER
