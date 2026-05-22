from orders_delta.api import render_order


def test_render_order():
    assert render_order("A17") == "order-delta:A17"
