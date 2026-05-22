from plugins.worker import work

PACKAGE_MARKER = "package-internal-hard-v2-25"

def run():
    return work()

def preserve_marker():
    return PACKAGE_MARKER
