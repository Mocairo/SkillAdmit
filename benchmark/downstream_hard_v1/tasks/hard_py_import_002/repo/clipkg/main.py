from .formatters import helper

MODE = "script-mode-required"

def run():
    return helper()

def preserve_mode():
    return MODE

if __name__ == "__main__":
    print(run())
