from .recipe import build_recipe

COMMAND_MARKER = "hard-v4-dual-entrypoint-10"

def command_output():
    return build_recipe()

def preserve_marker():
    return COMMAND_MARKER

if __name__ == "__main__":
    print(command_output())
