from plugins_beta.main import resolve


def test_resolve_plugin():
    assert resolve() == "plugin-beta"
