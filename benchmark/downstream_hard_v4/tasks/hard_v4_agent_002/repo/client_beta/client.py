import vendor_metrics_beta

CLIENT_MARKER = "hard-v4-optional-telemetry-2"

def format_event(event):
    return "evt-beta:" + str(event["id"]) + ":" + event.get("kind", "unknown")

def preserve_marker():
    return CLIENT_MARKER
