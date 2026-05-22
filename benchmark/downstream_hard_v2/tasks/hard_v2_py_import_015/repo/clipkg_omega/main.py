from .views import show

MODE = "script-mode-hard-v2-15"

def run():
    return show()

def preserve_mode():
    return MODE

if __name__ == "__main__":
    print(run())
