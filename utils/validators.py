def format_isbn13(isbn13: str) -> str:
    return f"{isbn13[:3]}-{isbn13[3:5]}-{isbn13[5:9]}-{isbn13[9:12]}-{isbn13[12]}"

def format_isbn10(isbn10: str) -> str:
    return f"{isbn10[0]}-{isbn10[1:4]}-{isbn10[4:9]}-{isbn10[9]}"

def format_isbn(isbn: str) -> str:
    if not isbn:
        return "N/A"
    if len(isbn) == 13:
        return format_isbn13(isbn)
    if len(isbn) == 10:
        return format_isbn10(isbn)
    return "N/A"
