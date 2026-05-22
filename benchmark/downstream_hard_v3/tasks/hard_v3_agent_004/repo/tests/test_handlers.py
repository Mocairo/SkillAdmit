from svc_delta.handlers import build_response


def test_build_response():
    assert build_response({"id": "42"}) == "delta-response:42"
