from registry.loader import load_plugin

PLUGIN_MARKER = "hard-v3-plugin-import-21"

def resolve():
    return load_plugin("alpha")

def preserve_marker():
    return PLUGIN_MARKER
