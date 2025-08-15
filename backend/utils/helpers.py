def extract_months(duration_str):
    # e.g., "3-month-old" → 3
    for word in duration_str.split():
        if word.isdigit():
            return int(word)
    return None
