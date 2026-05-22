import cloud_probe_gamma

SERVICE_MARKER = "hard-v3-optional-import-3"

def build_response(payload):
    return "gamma-response:" + str(payload["id"])

def preserve_marker():
    return SERVICE_MARKER
