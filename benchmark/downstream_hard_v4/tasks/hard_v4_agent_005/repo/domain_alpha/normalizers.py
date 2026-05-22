def normalize_slug(value):
    return "alpha-" + str(value).lower().replace(" ", "-")
