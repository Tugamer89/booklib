function formatISBN10(value) {
    return value.replace(/^(\d{0,1})(\d{0,3})(\d{0,5})(\d{0,1})$/, function(_, a, b, c, d) {
        return [a, b, c, d].filter(Boolean).join('-');
    });
}

function formatISBN13(value) {
    return value.replace(/^(\d{0,3})(\d{0,2})(\d{0,4})(\d{0,3})(\d{0,1})$/, function(_, a, b, c, d, e) {
        return [a, b, c, d, e].filter(Boolean).join('-');
    });
}

function formatISBN(inputOrEvent) {
    let raw;

    if (typeof inputOrEvent === 'string') {
        raw = inputOrEvent;
    } else if (inputOrEvent instanceof Event) {
        raw = inputOrEvent.target.value;
    } else if (inputOrEvent && typeof inputOrEvent.value === 'string') {
        raw = inputOrEvent.value;
    } else {
        console.error('formatISBN: input non valido');
        return '';
    }
    
    let value = raw.replace(/[^0-9X]/gi, '').toUpperCase();
    value = value.length <= 10 ? formatISBN10(value) : formatISBN13(value);

    if (inputOrEvent instanceof Event) inputOrEvent.target.value = value;
    else if (inputOrEvent && typeof inputOrEvent.value === 'string') inputOrEvent.value = value;

    return value;
}

function toggleVisibility(id, btn) {
    const el = document.getElementById(id);
    if (!el) return;

    const isHidden = el.style.display === "none" || getComputedStyle(el).display === "none";
    el.style.display = isHidden ? "block" : "none";

    const arrow = btn.querySelector(".arrow");
    if (arrow) arrow.textContent = isHidden ? "▲" : "▼";

    localStorage.setItem(id, isHidden);
    console.log(`Visibilità di ${id} impostata su ${isHidden}`);

    if (id === 'addForm' && isHidden) setTimeout(updateImageHeight, 50);
}

function formatLocation(input) {
    input.value = input.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
}

function onlyLettersNumbers(e) {
    const char = String.fromCharCode(e.which || e.keyCode);
    if (!/[a-zA-Z0-9]/.test(char)) {
        e.preventDefault();
        return false;
    }
    return true;
}

function validateLocation(input, errorSpanId) {
    const regex = /^[A-Z]+[0-9]+$/;
    const errorSpan = document.getElementById(errorSpanId);
    if (!regex.test(input.value)) {
        errorSpan.classList.remove('hidden');
        return false;
    } else {
        errorSpan.classList.add('hidden');
        return true;
    }
}

function validateAddForm() {
    const locationInput = document.getElementById('addLocation');
    return validateLocation(locationInput, 'addLocationError');
}

function validateFilterForm() {
    const locationInput = document.getElementById('filterLocation');
    return validateLocation(locationInput, 'filterLocationError');
}

function updateImageHeight() {
    const formFields = document.getElementById("formFields");
    const cover = document.getElementById("coverPreview");
    if (!formFields || !cover) return;

    const height = formFields.offsetHeight;
    cover.style.height = height + "px";
    cover.classList.remove('hidden');
}

function previewCover(event) {
    const img = document.getElementById("coverPreview");
    const file = event.target.files[0];
    if (file) {
        img.src = URL.createObjectURL(file);
        img.onload = updateImageHeight;
    }
}

window.addEventListener("load", updateImageHeight);
window.addEventListener("resize", updateImageHeight);

document.addEventListener("DOMContentLoaded", () => {
    ['addForm', 'filterForm'].forEach(id => {
        const el = document.getElementById(id);
        const btn = document.querySelector(`button[onclick*="${id}"]`);
        const arrow = btn ? btn.querySelector('.arrow') : null;

        const visible = localStorage.getItem(id) === 'true';

        if (el) el.style.display = visible ? 'block' : 'none';
        if (arrow) arrow.textContent = visible ? '▲' : '▼';

        if (id === 'addForm' && visible) updateImageHeight();
    });
});
