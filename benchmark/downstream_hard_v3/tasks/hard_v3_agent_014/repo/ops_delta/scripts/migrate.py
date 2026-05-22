from .payload import build_payload

COMMAND_MARKER = "hard-v3-dual-command-14"

def command_output():
    return build_payload()

def preserve_marker():
    return COMMAND_MARKER

if __name__ == "__main__":
    print(command_output())
