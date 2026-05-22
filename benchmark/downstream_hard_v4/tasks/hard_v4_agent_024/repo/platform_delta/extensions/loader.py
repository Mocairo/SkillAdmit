def load_plugin(name):
    if name == "delta":
        return "plugin-delta"
    raise KeyError(name)
