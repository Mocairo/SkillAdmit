def load_plugin(name):
    if name == "omega":
        return "plugin-omega"
    raise KeyError(name)
