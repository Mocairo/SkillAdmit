from .tools import format_value

MODE = "script-mode-hard-v2-12"

def run():
    return format_value()

def preserve_mode():
    return MODE

if __name__ == "__main__":
    print(run())
