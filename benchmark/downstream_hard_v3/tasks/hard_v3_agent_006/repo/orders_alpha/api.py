from formatters import format_order

API_MARKER = "hard-v3-local-import-6"

def render_order(order_id):
    return format_order(order_id)

def preserve_marker():
    return API_MARKER
