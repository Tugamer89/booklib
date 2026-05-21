function formatISBN10(value) {
    return value.replaceAll(/^(\d)(\d{3})(\d{5})(\d|X)$/g, "$1-$2-$3-$4");
}
function formatISBN13(value) {
    return value.replaceAll(/^(\d{3})(\d)(\d{2})(\d{6})(\d)$/g, "$1-$2-$3-$4-$5");
}
export function formatISBN(isbn) {
    if (!isbn) return "N/D";
    const cleaned = String(isbn)
        .replaceAll(/[^0-9X]/gi, "")
        .toUpperCase();
    if (cleaned.length === 10) {
        return formatISBN10(cleaned);
    }
    if (cleaned.length === 13) {
        return formatISBN13(cleaned);
    }
    return isbn;
}
function liveFormatISBN10(value) {
    return value.replaceAll(/^(\d?)(\d{0,3})(\d{0,5})(\d?)$/g, function (_, a, b, c, d) {
        return [a, b, c, d].filter(Boolean).join("-");
    });
}
function liveFormatISBN13(value) {
    return value.replaceAll(
        /^(\d{0,3})(\d?)(\d{0,2})(\d{0,6})(\d?})$/g,
        function (_, a, b, c, d, e) {
            return [a, b, c, d, e].filter(Boolean).join("-");
        }
    );
}
export function liveFormatISBN(value) {
    const cleaned = value.replaceAll(/[^0-9X]/gi, "").toUpperCase();
    if (cleaned.length <= 10) {
        return liveFormatISBN10(cleaned);
    } else {
        return liveFormatISBN13(cleaned.substring(0, 13));
    }
}
