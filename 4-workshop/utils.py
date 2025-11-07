def debug(message, source=""):
    """Print debug message with optional source prefix."""
    if source:
        print(f"[{source}] {message}")
    else:
        print(message)