from domain_alpha.service import build_slug


def test_build_slug():
    assert build_slug("Alpha Case") == "alpha-alpha-case"
