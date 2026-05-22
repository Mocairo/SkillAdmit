from plugins_alpha.main import resolve


def test_resolve_plugin():
    assert resolve() == "plugin-alpha"
