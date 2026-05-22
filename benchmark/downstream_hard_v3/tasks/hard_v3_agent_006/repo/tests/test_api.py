from orders_alpha.api import render_order


def test_render_order():
    assert render_order("A17") == "order-alpha:A17"
