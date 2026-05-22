from catalog.loader import load_plugin

PLUGIN_MARKER = "hard-v4-plugin-registry-22"

def resolve_plugin():
    return load_plugin("beta")

def preserve_marker():
    return PLUGIN_MARKER
