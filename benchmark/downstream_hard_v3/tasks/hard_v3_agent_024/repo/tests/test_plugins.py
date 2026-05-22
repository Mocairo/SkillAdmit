from plugins_delta.main import resolve


def test_resolve_plugin():
    assert resolve() == "plugin-delta"
