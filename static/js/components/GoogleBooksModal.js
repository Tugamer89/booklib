import { ref, onMounted, computed } from "vue";
import BookSearchResult from "./BookSearchResult.js";

// Global cache for Google Books API responses to reduce redundant network requests across modal opens
const searchCache = new Map();

export default {
    name: "GoogleBooksModal",
    components: { BookSearchResult },
    props: ["isVisible", "initialSearchTerms"],
    emits: ["close", "book-selected"],
    setup(props, { emit }) {
        const results = ref([]);
        const isLoading = ref(false);
        const isLoadingMore = ref(false);
        const error = ref(null);
        const startIndex = ref(0);
        const totalItems = ref(0);
        const resultsContainer = ref(null);

        const formattedQuery = computed(() => {
            const { title, author, isbn } = props.initialSearchTerms;
            const parts = [];
            if (title) parts.push(`Title: "${title}"`);
            if (author) parts.push(`Author: "${author}"`);
            if (isbn && isbn !== "N/A") parts.push(`ISBN: "${isbn}"`);
            return parts.join(", ") || "No search terms entered";
        });

        const buildQuery = (terms) => {
            const { title, author, isbn } = terms;
            const parts = [];
            if (title) parts.push(`intitle:${encodeURIComponent(title)}`);
            if (author) parts.push(`inauthor:${encodeURIComponent(author)}`);
            if (isbn && isbn !== "N/A")
                parts.push(`isbn:${encodeURIComponent(isbn.replaceAll("-", ""))}`);
            return parts.join("+");
        };

        const fetchSearchResults = async (query, startIdx) => {
            const cacheKey = `${query}-${startIdx}`;
            if (searchCache.has(cacheKey)) {
                return searchCache.get(cacheKey);
            }

            const response = await fetch(
                `/api/search-google-books?q=${encodeURIComponent(query)}&max_results=20&start_index=${startIdx}`
            );
            if (!response.ok) {
                const errorMessage = await extractErrorMessage(response);
                throw new Error(errorMessage);
            }
            const data = await response.json();
            searchCache.set(cacheKey, data);
            return data;
        };

        const search = async (loadMore = false) => {
            const finalQuery = buildQuery(props.initialSearchTerms);

            if (!finalQuery) {
                error.value =
                    "Please enter at least one search term (title, author or ISBN) in the form.";
                return;
            }

            if (loadMore) {
                if (isLoadingMore.value || results.value.length >= totalItems.value) return;
                isLoadingMore.value = true;
            } else {
                isLoading.value = true;
                results.value = [];
                startIndex.value = 0;
            }
            error.value = null;

            try {
                const data = await fetchSearchResults(finalQuery, startIndex.value);

                totalItems.value = data.totalItems || 0;
                const newItems = data.items || [];
                if (loadMore) {
                    results.value.push(...newItems);
                } else {
                    results.value = newItems;
                }

                startIndex.value += newItems.length;
                if (!loadMore && newItems.length === 0)
                    error.value = "No books found for this search.";
            } catch (err) {
                error.value = err.message;
            } finally {
                isLoading.value = false;
                isLoadingMore.value = false;
            }
        };

        onMounted(() => {
            search(false);
        });

        const handleScroll = () => {
            const el = resultsContainer.value;
            if (!el) return;
            const isAtBottom = el.scrollTop + el.clientHeight >= el.scrollHeight - 150;
            if (isAtBottom && results.value.length < totalItems.value) {
                search(true);
            }
        };

        const selectBook = (book) => {
            const info = book.volumeInfo;
            const isbn13 = info.industryIdentifiers?.find(
                (id) => id.type === "ISBN_13"
            )?.identifier;
            const isbn10 = info.industryIdentifiers?.find(
                (id) => id.type === "ISBN_10"
            )?.identifier;
            const selectedData = {
                title: info.title || "",
                author: (info.authors || []).join(", "),
                publisher: info.publisher || "",
                description: info.description || "",
                language: info.language || "",
                isbn: isbn13 || isbn10 || "",
                cover_url: info.imageLinks?.thumbnail?.replace("http:", "https:") || "",
            };
            emit("book-selected", selectedData);
            close();
        };

        const close = () => emit("close");

        return {
            results,
            isLoading,
            isLoadingMore,
            error,
            formattedQuery,
            resultsContainer,
            search,
            selectBook,
            close,
            handleScroll,
            startIndex,
        };
    },
    template: `
        <transition name="fade" appear>
            <div class="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" @click.self="close">
                <div class="bg-white dark:bg-slate-800 rounded-lg shadow-xl w-full max-w-3xl h-[80vh] flex flex-col">
                    <div class="p-4 border-b dark:border-slate-700 flex-shrink-0">
                        <div class="flex justify-between items-center">
                            <div>
                                <h3 class="text-xl font-bold text-slate-800 dark:text-slate-100">Results for:</h3>
                                <p class="text-sm text-slate-500 dark:text-slate-400 truncate">{{ formattedQuery }}</p>
                            </div>
                            <button @click="close" class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-2xl" aria-label="Close modal">&times;</button>
                        </div>
                    </div>
                    <div ref="resultsContainer" @scroll="handleScroll" class="overflow-y-auto p-4 flex-grow">
                        <div v-if="isLoading" class="text-center text-slate-500">Loading...</div>
                        <div v-else-if="error" class="text-center text-red-500">{{ error }}</div>
                        <div v-else-if="results.length > 0">
                            <div class="space-y-3">
                                <BookSearchResult v-for="(book, index) in results" :key="book.id + '-' + index" :book="book" @select="selectBook" />
                            </div>
                            <div v-if="isLoadingMore" class="text-center text-slate-500 mt-4">Loading more results...</div>
                        </div>
                         <div v-else class="text-center text-slate-500 pt-8">Use the search to find a book.</div>
                    </div>
                </div>
            </div>
        </transition>
    `,
};

async function extractErrorMessage(response) {
    const data = await response.json().catch(() => null);

    if (data?.error?.message?.includes("Quota exceeded")) {
        return "Google Books API search quota exceeded. Please try again later or add the book manually.";
    }

    return data?.error?.message ? `Search error: ${data.error.message}` : "Search error.";
}
