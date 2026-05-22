from serializers import serialize_order

API_MARKER = "hard-v3-local-import-7"

def render_order(order_id):
    return serialize_order(order_id)

def preserve_marker():
    return API_MARKER
