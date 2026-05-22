from domain_gamma.service import build_slug


def test_build_slug():
    assert build_slug("Alpha Case") == "gamma-alpha-case"
