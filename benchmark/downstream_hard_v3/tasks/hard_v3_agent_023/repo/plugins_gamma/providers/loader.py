def load_plugin(name):
    if name == "gamma":
        return "plugin-gamma"
    raise KeyError(name)
