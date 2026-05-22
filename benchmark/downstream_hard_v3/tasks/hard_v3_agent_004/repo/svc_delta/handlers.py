import vendor_audit_delta

SERVICE_MARKER = "hard-v3-optional-import-4"

def build_response(payload):
    return "delta-response:" + str(payload["id"])

def preserve_marker():
    return SERVICE_MARKER
