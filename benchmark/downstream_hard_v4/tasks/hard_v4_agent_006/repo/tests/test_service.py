from domain_beta.service import build_slug


def test_build_slug():
    assert build_slug("Alpha Case") == "beta-alpha-case"
