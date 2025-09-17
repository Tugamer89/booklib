let currentOffset = 0;
let isLoading = false;
let hasMore = true;
const offsetSize = 20;

async function loadBooks(reset = false) {
    if (isLoading || !hasMore) return;
    isLoading = true;

    let tableBody = document.getElementById("bookRows");
    
    if (reset) {
        currentOffset = 0;
        hasMore = true;
    }

    const params = new URLSearchParams(window.location.search);
    params.set("offset", currentOffset);
    params.set("limit", offsetSize);
    params.set("_", Date.now());

    try {
        const res = await fetch(`/books-data?${params.toString()}`, {
            headers: { "X-Requested-With": "XMLHttpRequest" }
        });

        if (!res.ok) throw new Error("Errore fetch libri");

        const data = await res.json();
        const books = data.books || [];

        const fragment = document.createDocumentFragment();

        books.forEach(book => {
            const row = document.createElement("tr");
            row.dataset.book = JSON.stringify(book);
            
            row.onclick = (event) => {
                event.stopPropagation();
                const bookData = JSON.parse(row.dataset.book);
                openDetailModal(bookData);
            };
            
            row.className = "border-t hover:bg-gray-50 transition group";
            row.innerHTML = `
                <td class="p-2 max-w-xs">
                    <img src="${book.cover_path}" alt="Copertina di ${book.title}" 
                         class="h-24 rounded shadow-sm" loading="lazy">
                </td>
                <td class="p-2 break-words max-w-xs">${book.title}</td>
                <td class="p-2 break-words max-w-xs">${book.author}</td>
                <td class="p-2 break-words">${formatISBN(book.isbn) || "N/A"}</td>
                <td class="p-2 break-words max-w-xs">${book.publisher}</td>
                <td class="p-2 break-words [text-indent:15%]">${book.location}</td>
                <td class="p-2 text-center space-x-2 group">
                    <div class="flex items-center justify-center space-x-3 opacity-0 transition-opacity duration-200 group-hover:opacity-100">
                        <button type="button" 
                            class="edit-btn text-indigo-600 hover:text-indigo-900 text-xl font-bold">
                            ✎
                        </button>
                        <form method="post" action="/delete">
                            <input type="hidden" name="book_id" value="${book.id}">
                            <button type="submit"
                                    onclick="event.stopPropagation();"
                                    class="delete-btn text-red-600 hover:text-red-800 text-2xl font-bold">
                                &times;
                            </button>
                        </form>
                    </div>
                </td>
            `;

            row.querySelector(".edit-btn").onclick = (event) => {
                event.stopPropagation();
                const bookData = JSON.parse(row.dataset.book);
                openEditModal(bookData);
            };

            fragment.appendChild(row);
        });

        if (reset) {
            tableBody.replaceChildren(fragment);
        } else {
            tableBody.appendChild(fragment);
        }

        hasMore = data.has_more;
        if (hasMore) currentOffset += offsetSize;
    } catch (e) {
        console.error("Errore caricamento libri:", e);
    } finally {
        isLoading = false;
    }
}

window.addEventListener("scroll", () => {
    if (isLoading || !hasMore) return;

    const scrollPosition = window.innerHeight + window.scrollY;
    const pageHeight = document.documentElement.scrollHeight;
    
    if (scrollPosition >= pageHeight * 0.9) loadBooks();
});

document.addEventListener("DOMContentLoaded", () => {
    loadBooks(true);
});

window.addEventListener("sortChanged", () => {
    loadBooks(true);
});
