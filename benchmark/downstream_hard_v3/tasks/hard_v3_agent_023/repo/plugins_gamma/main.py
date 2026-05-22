from providers.loader import load_plugin

PLUGIN_MARKER = "hard-v3-plugin-import-23"

def resolve():
    return load_plugin("gamma")

def preserve_marker():
    return PLUGIN_MARKER
