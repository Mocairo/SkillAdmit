import optional_metrics_alpha

SERVICE_MARKER = "hard-v3-optional-import-1"

def build_response(payload):
    return "alpha-response:" + str(payload["id"])

def preserve_marker():
    return SERVICE_MARKER
