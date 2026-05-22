from workers.worker import work

PACKAGE_MARKER = "package-internal-hard-v2-24"

def run():
    return work()

def preserve_marker():
    return PACKAGE_MARKER
