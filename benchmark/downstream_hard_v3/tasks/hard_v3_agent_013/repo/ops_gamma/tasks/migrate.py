from .layout import build_layout

COMMAND_MARKER = "hard-v3-dual-command-13"

def command_output():
    return build_layout()

def preserve_marker():
    return COMMAND_MARKER

if __name__ == "__main__":
    print(command_output())
