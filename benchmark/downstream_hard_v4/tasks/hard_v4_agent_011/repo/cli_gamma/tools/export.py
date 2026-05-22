from .summary import build_summary

COMMAND_MARKER = "hard-v4-dual-entrypoint-11"

def command_output():
    return build_summary()

def preserve_marker():
    return COMMAND_MARKER

if __name__ == "__main__":
    print(command_output())
