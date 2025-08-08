def format_isbn13(isbn13: str) -> str:
    if not isbn13:
        return "N/A"
    return f"{isbn13[:3]}-{isbn13[3:5]}-{isbn13[5:9]}-{isbn13[9:12]}-{isbn13[12]}"
