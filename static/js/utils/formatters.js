function formatISBN10(value) {
    return value.replace(/^(\d{1})(\d{3})(\d{5})(\d{1}|X)$/, '$1-$2-$3-$4');
}

function formatISBN13(value) {
    return value.replace(/^(\d{3})(\d{1})(\d{2})(\d{6})(\d{1})$/, '$1-$2-$3-$4-$5');
}

export function formatISBN(isbn) {
    if (!isbn) return 'N/D';
    const cleaned = String(isbn).replace(/[^0-9X]/gi, '').toUpperCase();
    if (cleaned.length === 10) {
        return formatISBN10(cleaned);
    }
    if (cleaned.length === 13) {
        return formatISBN13(cleaned);
    }
    return isbn;
}

function liveFormatISBN10(value) {
    return value.replace(/^(\d{0,1})(\d{0,3})(\d{0,5})(\d{0,1})$/, function(_, a, b, c, d) {
        return [a, b, c, d].filter(Boolean).join('-');
    });
}

function liveFormatISBN13(value) {
    return value.replace(/^(\d{0,3})(\d{0,1})(\d{0,2})(\d{0,6})(\d{0,1})$/, function(_, a, b, c, d, e) {
        return [a, b, c, d, e].filter(Boolean).join('-');
    });
}

export function liveFormatISBN(value) {
    const cleaned = value.replace(/[^0-9X]/gi, '').toUpperCase();
    if (cleaned.length <= 10) {
        return liveFormatISBN10(cleaned);
    } else {
        return liveFormatISBN13(cleaned.substring(0, 13));
    }
}