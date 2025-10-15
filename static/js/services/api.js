async function fetchApi(url, options = {}) {
    try {
        const response = await fetch(url, options);
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'Errore sconosciuto' }));
            throw new Error(errorData.detail || `Errore: ${response.statusText}`);
        }
        return response.json();
    } catch (error) {
        console.error('Errore API:', error);
        throw error;
    }
}

export const api = {
    getBooks: (params) => {
        const urlParams = new URLSearchParams(params);
        return fetchApi(`/books-data?${urlParams}`);
    }
};