def load_plugin(name):
    if name == "alpha":
        return "plugin-alpha"
    raise KeyError(name)
