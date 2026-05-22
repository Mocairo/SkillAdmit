from svc_alpha.handlers import build_response


def test_build_response():
    assert build_response({"id": "42"}) == "alpha-response:42"
