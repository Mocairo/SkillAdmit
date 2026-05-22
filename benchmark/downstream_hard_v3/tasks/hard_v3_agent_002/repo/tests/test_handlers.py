from svc_beta.handlers import build_response


def test_build_response():
    assert build_response({"id": "42"}) == "beta-response:42"
