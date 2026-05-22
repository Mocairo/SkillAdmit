from summaries import summarize_order

API_MARKER = "hard-v3-local-import-9"

def render_order(order_id):
    return summarize_order(order_id)

def preserve_marker():
    return API_MARKER
