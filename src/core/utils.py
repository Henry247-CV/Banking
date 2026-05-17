def safe_currency(amount):
    """Safely formats a number into VND currency format."""
    try:
        if amount is None:
            return "0 VND"
        return "{:,.0f} VND".format(float(amount))
    except (ValueError, TypeError):
        return "0 VND"

def safe_text(text, default="N/A"):
    """Safely returns text or a default value if None or empty."""
    if text is None or str(text).strip() == "":
        return default
    return str(text).strip()

def safe_int(value, default=0):
    """Safely converts a value to an integer."""
    try:
        if value is None:
            return default
        return int(float(value))
    except (ValueError, TypeError):
        return default
