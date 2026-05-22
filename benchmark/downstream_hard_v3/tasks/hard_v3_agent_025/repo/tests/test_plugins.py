from plugins_omega.main import resolve


def test_resolve_plugin():
    assert resolve() == "plugin-omega"
