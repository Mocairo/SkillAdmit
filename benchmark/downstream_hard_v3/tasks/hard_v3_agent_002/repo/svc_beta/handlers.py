import future_tracing_beta

SERVICE_MARKER = "hard-v3-optional-import-2"

def build_response(payload):
    return "beta-response:" + str(payload["id"])

def preserve_marker():
    return SERVICE_MARKER
