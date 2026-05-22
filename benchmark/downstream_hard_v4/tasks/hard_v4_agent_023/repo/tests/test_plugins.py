from platform_gamma.main import resolve_plugin


def test_resolve_plugin():
    assert resolve_plugin() == "plugin-gamma"
