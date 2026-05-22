from .plan import build_plan

COMMAND_MARKER = "hard-v4-dual-entrypoint-12"

def command_output():
    return build_plan()

def preserve_marker():
    return COMMAND_MARKER

if __name__ == "__main__":
    print(command_output())
