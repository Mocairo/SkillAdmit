from adapters.loader import load_plugin

PLUGIN_MARKER = "hard-v3-plugin-import-25"

def resolve():
    return load_plugin("omega")

def preserve_marker():
    return PLUGIN_MARKER
