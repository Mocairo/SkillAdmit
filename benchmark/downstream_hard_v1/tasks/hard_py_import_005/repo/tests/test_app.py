from app import get_name

def test_get_name():
    assert get_name() == "hard-unused-import-ok"
