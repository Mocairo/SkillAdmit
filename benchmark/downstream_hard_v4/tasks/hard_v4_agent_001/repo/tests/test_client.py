from client_alpha.client import format_event


def test_format_event_without_optional_telemetry():
    assert format_event({"id": "42", "kind": "audit"}) == "evt-alpha:42:audit"
