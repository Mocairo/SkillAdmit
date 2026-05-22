import cloud_probe_gamma

CLIENT_MARKER = "hard-v4-optional-telemetry-3"

def format_event(event):
    return "evt-gamma:" + str(event["id"]) + ":" + event.get("kind", "unknown")

def preserve_marker():
    return CLIENT_MARKER
