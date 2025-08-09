let currentQuery = '';
let language = '';
let currentStartIndex = 0;
let totalItems = 0;
let isLoading = false;

function getInput(name) {
    return document.querySelector(`input[name="${name}"]`);
}

function validateSearchInputs() {
    const fields = ['titleAdd', 'authorAdd', 'isbnAdd', 'publisherAdd'];
    return fields.some(name => {
        const el = document.getElementById(name);
        return el && el.value.trim() !== '';
    });
}

function showError(message) {
    alert(message);
}

async function fetchBooksFromGoogle(query, startIndex = 0, language = '') {
    let url = `https://www.googleapis.com/books/v1/volumes?q=${encodeURIComponent(query)}&maxResults=10&startIndex=${startIndex}`;
    if (language && /^[a-zA-Z]{2,3}$/i.test(language)) url += `&langRestrict=${language.toLowerCase()}`;
    const response = await fetch(url);
    if (!response.ok) throw new Error('Errore nel fetch di Google Books');
    const data = await response.json();
    return data;
}

function createBookItem(book) {
    const info = book.volumeInfo;
    const volumeId = book.id;

    const title = info.title || '';
    const authors = (info.authors || []).join(', ');
    const publisher = info.publisher || '';
    const publishedDate = info.publishedDate || '';
    const description = info.description || '';
    const language = info.language || '';

    const thumbnail = volumeId
        ? `https://books.google.com/books/publisher/content/images/frontcover/${volumeId}?fife=w500&source=gbs_api`
        : (info.imageLinks?.thumbnail || '');

    let isbn = '';
    if (info.industryIdentifiers) {
        const isbn13 = info.industryIdentifiers.find(id => id.type === 'ISBN_13');
        const isbn10 = info.industryIdentifiers.find(id => id.type === 'ISBN_10');
        isbn = (isbn13 || isbn10)?.identifier || '';
    }

    const div = document.createElement('div');
    div.className = 'border rounded p-4 flex gap-4 items-center';

    div.innerHTML = `
        <img src="${thumbnail}" alt="Copertina" class="w-20 h-28 object-contain rounded border"/>
        <div class="flex-1">
            <h3 class="font-bold">${title}</h3>
            <p class="text-sm text-gray-600">${authors}</p>
            <p class="text-sm">${publisher} ${publishedDate}</p>
            <p class="text-xs mt-1 line-clamp-3">${description}</p>
            <p class="text-xs mt-1 font-mono">ISBN: ${isbn}</p>
            <p class="text-xs mt-1 font-mono">Lingua: ${language.toUpperCase()}</p>
        </div>
        <button class="selectBookBtn px-3 py-1 bg-blue-500 hover:bg-blue-600 text-white rounded">Seleziona</button>
    `;

    div.querySelector('.selectBookBtn').addEventListener('click', () => {
        populateFormWithBook({
            title,
            authors,
            publisher,
            isbn,
            thumbnail,
            description,
            language
        });
        closePopup();
    });

    return div;
}

function populateFormWithBook({title, authors, publisher, isbn, thumbnail, description, language}) {
    const titleInput = document.getElementById("titleAdd");
    const authorInput = document.getElementById("authorAdd");
    const publisherInput = document.getElementById("publisherAdd");
    const isbnInput = document.getElementById("isbnAdd");
    const cover_urlInput = document.getElementById("cover_url");
    const descriptionInput = document.querySelector('textarea[name="description"]');
    const languageInput = document.getElementById("languageAdd");

    if (!titleInput || !authorInput || !publisherInput || !isbnInput || !cover_urlInput || !descriptionInput || !languageInput) return;

    titleInput.value = title || '';
    authorInput.value = authors || '';
    publisherInput.value = publisher || '';
    isbnInput.value = formatISBN(isbn || '');
    cover_urlInput.value = thumbnail || '';
    descriptionInput.value = description || '';
    languageInput.value = validateLanguage(language || '');

    const coverPreview = document.getElementById('coverPreview');
    if (thumbnail) {
        coverPreview.src = thumbnail.replace(/^http:\/\//i, 'https://');
    } else {
        coverPreview.src = '/static/covers/default.jpg';
    }

    updateImageHeight();
}

function openPopup() {
    const popup = document.getElementById('searchPopup');
    popup.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

function closePopup() {
    const popup = document.getElementById('searchPopup');
    popup.classList.add('hidden');
    document.body.style.overflow = '';
    document.getElementById('booksList').innerHTML = '';

    currentQuery = '';
    language = '';
    currentStartIndex = 0;
    totalItems = 0;
}

async function onSearchButtonClick() {
    if (!validateSearchInputs()) {
        showError('Inserisci almeno un campo di ricerca prima di cercare.');
        return;
    }

    const fieldMap = {
        titleAdd: 'intitle',
        authorAdd: 'inauthor',
        isbnAdd: 'isbn',
        publisherAdd: 'inpublisher'
    };

    currentQuery = Object.entries(fieldMap).map(([name, prefix]) => {
        const el = document.getElementById(name);
        const value = el ? el.value.trim() : '';
        return value ? `${prefix}:${value}` : '';
    }).filter(Boolean).join(' ');

    const langInput = document.getElementById('languageAdd');
    language = (langInput && /^[A-Za-z]{2,3}$/.test(langInput.value.trim())) ? langInput.value.trim().toLowerCase() : '';

    currentStartIndex = 0;
    totalItems = 0;

    openPopup();

    const booksList = document.getElementById('booksList');
    booksList.innerHTML = '<p>Caricamento...</p>';

    try {
        isLoading = true;
        const data = await fetchBooksFromGoogle(currentQuery, currentStartIndex, language);
        totalItems = data.totalItems || 0;
        booksList.innerHTML = '';

        if (!data.items || data.items.length === 0) {
            booksList.innerHTML = '<p>Nessun risultato trovato.</p>';
            return;
        }

        data.items.forEach(book => {
            const item = createBookItem(book);
            booksList.appendChild(item);
        });

        currentStartIndex += data.items.length;
        isLoading = false;
    } catch(e) {
        isLoading = false;
        booksList.innerHTML = `<p class="text-red-600">Errore durante la ricerca: ${e.message}</p>`;
    }
}

async function scrollerLoading() {
    const el = this;

    if (isLoading) return;
    if (currentStartIndex >= totalItems) return;

    if (el.scrollTop + el.clientHeight >= el.scrollHeight * 0.9) {
        isLoading = true;

        const loadingIndicator = document.createElement('p');
        loadingIndicator.textContent = 'Caricamento...';
        loadingIndicator.id = 'loadingIndicator';
        el.appendChild(loadingIndicator);

        try {
            const data = await fetchBooksFromGoogle(currentQuery, currentStartIndex, language);
            if (data.items && data.items.length > 0) {
                data.items.forEach(book => {
                    const item = createBookItem(book);
                    el.appendChild(item);
                });
                currentStartIndex += data.items.length;
            }
        } catch(e) {
            console.error('Errore caricamento libri:', e);
        } finally {
            isLoading = false;
            const loadingEl = document.getElementById('loadingIndicator');
            if (loadingEl) loadingEl.remove();
        }
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const closeBtn = document.getElementById('closePopup');
    if (closeBtn) closeBtn.addEventListener('click', closePopup);

    const searchBtn = document.getElementById('search');
    if (searchBtn) searchBtn.addEventListener('click', onSearchButtonClick);

    const coverInput = document.getElementById('cover');
    const coverUrlInput = document.getElementById("cover_url");

    if (coverInput && coverUrlInput) {
        coverInput.addEventListener("change", () => {
            coverUrlInput.value = "";
        });
    }

    const booksList = document.getElementById('booksList');
    if (booksList) booksList.addEventListener('scroll', scrollerLoading);
});
