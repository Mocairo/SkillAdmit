from .payload import build_payload

COMMAND_MARKER = "hard-v4-dual-entrypoint-9"

def command_output():
    return build_payload()

def preserve_marker():
    return COMMAND_MARKER

if __name__ == "__main__":
    print(command_output())
