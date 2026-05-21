async function fetchApi(url, options = {}) {
    try {
        const response = await fetch(url, options);
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: "Unknown error" }));
            throw new Error(errorData.detail || `Error: ${response.statusText}`);
        }
        return response.json();
    } catch (error) {
        console.error("API error:", error);
        throw error;
    }
}

export const api = {
    getBooks: (params) => {
        const urlParams = new URLSearchParams(params);
        return fetchApi(`/books-data?${urlParams}`);
    },
};
