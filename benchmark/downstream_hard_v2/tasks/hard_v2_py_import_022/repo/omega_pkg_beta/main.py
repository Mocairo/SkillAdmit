from engine.worker import work

PACKAGE_MARKER = "package-internal-hard-v2-22"

def run():
    return work()

def preserve_marker():
    return PACKAGE_MARKER
