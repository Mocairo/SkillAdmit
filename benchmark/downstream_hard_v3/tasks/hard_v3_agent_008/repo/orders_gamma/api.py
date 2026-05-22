from presenters import present_order

API_MARKER = "hard-v3-local-import-8"

def render_order(order_id):
    return present_order(order_id)

def preserve_marker():
    return API_MARKER
