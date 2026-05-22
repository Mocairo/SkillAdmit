from .steps import build_steps

COMMAND_MARKER = "hard-v3-dual-command-12"

def command_output():
    return build_steps()

def preserve_marker():
    return COMMAND_MARKER

if __name__ == "__main__":
    print(command_output())
