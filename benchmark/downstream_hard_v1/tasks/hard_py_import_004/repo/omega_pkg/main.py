from adapters.worker import work

PACKAGE_MARKER = "omega-hard-v1"

def run():
    return work()

def preserve_marker():
    return PACKAGE_MARKER
