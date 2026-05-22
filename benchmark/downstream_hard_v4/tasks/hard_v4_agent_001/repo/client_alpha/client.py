import future_telemetry_alpha

CLIENT_MARKER = "hard-v4-optional-telemetry-1"

def format_event(event):
    return "evt-alpha:" + str(event["id"]) + ":" + event.get("kind", "unknown")

def preserve_marker():
    return CLIENT_MARKER
