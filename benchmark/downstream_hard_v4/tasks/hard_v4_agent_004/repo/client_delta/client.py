import audit_sink_delta

CLIENT_MARKER = "hard-v4-optional-telemetry-4"

def format_event(event):
    return "evt-delta:" + str(event["id"]) + ":" + event.get("kind", "unknown")

def preserve_marker():
    return CLIENT_MARKER
