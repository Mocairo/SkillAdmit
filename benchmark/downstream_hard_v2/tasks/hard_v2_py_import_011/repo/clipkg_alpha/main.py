from .formatters import render

MODE = "script-mode-hard-v2-11"

def run():
    return render()

def preserve_mode():
    return MODE

if __name__ == "__main__":
    print(run())
