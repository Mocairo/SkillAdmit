from labels import label_order

API_MARKER = "hard-v3-local-import-10"

def render_order(order_id):
    return label_order(order_id)

def preserve_marker():
    return API_MARKER
