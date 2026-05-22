from svc_gamma.handlers import build_response


def test_build_response():
    assert build_response({"id": "42"}) == "gamma-response:42"
