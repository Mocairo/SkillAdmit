from platform_alpha.main import resolve_plugin


def test_resolve_plugin():
    assert resolve_plugin() == "plugin-alpha"
