def load_plugin(name):
    if name == "beta":
        return "plugin-beta"
    raise KeyError(name)
