from registry.loader import load_plugin

PLUGIN_MARKER = "hard-v4-plugin-registry-21"

def resolve_plugin():
    return load_plugin("alpha")

def preserve_marker():
    return PLUGIN_MARKER
