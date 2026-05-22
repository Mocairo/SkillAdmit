import telemetry_omega_sdk

SERVICE_MARKER = "hard-v3-optional-import-5"

def build_response(payload):
    return "omega-response:" + str(payload["id"])

def preserve_marker():
    return SERVICE_MARKER
