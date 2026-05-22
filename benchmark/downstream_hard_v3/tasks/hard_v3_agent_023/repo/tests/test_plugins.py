from plugins_gamma.main import resolve


def test_resolve_plugin():
    assert resolve() == "plugin-gamma"
