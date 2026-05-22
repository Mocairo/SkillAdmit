from domain_delta.service import build_slug


def test_build_slug():
    assert build_slug("Alpha Case") == "delta-alpha-case"
