from providers.loader import load_plugin

PLUGIN_MARKER = "hard-v4-plugin-registry-23"

def resolve_plugin():
    return load_plugin("gamma")

def preserve_marker():
    return PLUGIN_MARKER
