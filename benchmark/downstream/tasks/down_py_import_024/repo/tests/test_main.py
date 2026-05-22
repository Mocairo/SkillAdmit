from delta_pkg.main import run

def test_run():
    assert run() == "internal-delta-ok"
