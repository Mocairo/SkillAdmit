from extensions.loader import load_plugin

PLUGIN_MARKER = "hard-v4-plugin-registry-24"

def resolve_plugin():
    return load_plugin("delta")

def preserve_marker():
    return PLUGIN_MARKER
