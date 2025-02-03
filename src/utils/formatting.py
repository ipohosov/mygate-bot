def format_number(num):
    return f"{num:,.2f}" if isinstance(num, float) else f"{num:,}"
