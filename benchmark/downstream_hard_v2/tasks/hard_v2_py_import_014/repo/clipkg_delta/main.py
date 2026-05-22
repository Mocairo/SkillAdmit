from .serializers import serialize

MODE = "script-mode-hard-v2-14"

def run():
    return serialize()

def preserve_mode():
    return MODE

if __name__ == "__main__":
    print(run())
