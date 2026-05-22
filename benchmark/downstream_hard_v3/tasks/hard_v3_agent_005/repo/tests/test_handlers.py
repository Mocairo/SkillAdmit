from svc_omega.handlers import build_response


def test_build_response():
    assert build_response({"id": "42"}) == "omega-response:42"
