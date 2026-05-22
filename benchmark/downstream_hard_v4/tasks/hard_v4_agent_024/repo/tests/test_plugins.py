from platform_delta.main import resolve_plugin


def test_resolve_plugin():
    assert resolve_plugin() == "plugin-delta"
