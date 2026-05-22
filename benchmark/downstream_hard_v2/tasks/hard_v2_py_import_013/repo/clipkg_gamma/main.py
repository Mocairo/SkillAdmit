from .helpers import make_output

MODE = "script-mode-hard-v2-13"

def run():
    return make_output()

def preserve_mode():
    return MODE

if __name__ == "__main__":
    print(run())
