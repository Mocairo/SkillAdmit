from orders_omega.api import render_order


def test_render_order():
    assert render_order("A17") == "order-omega:A17"
