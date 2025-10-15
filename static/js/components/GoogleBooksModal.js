import { ref, onMounted, computed } from 'vue';
import BookSearchResult from './BookSearchResult.js';

export default {
    name: 'GoogleBooksModal',
    components: { BookSearchResult },
    props: ['isVisible', 'initialSearchTerms'],
    emits: ['close', 'book-selected'],
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
            if (title) parts.push(`Titolo: "${title}"`);
            if (author) parts.push(`Autore: "${author}"`);
            if (isbn) parts.push(`ISBN: "${isbn}"`);
            return parts.join(', ') || 'Nessun termine inserito';
        });

        const search = async (loadMore = false) => {
            const { title, author, isbn } = props.initialSearchTerms;
            const queryParts = [];
            if (title) queryParts.push(`intitle:${encodeURIComponent(title)}`);
            if (author) queryParts.push(`inauthor:${encodeURIComponent(author)}`);
            if (isbn) queryParts.push(`isbn:${encodeURIComponent(isbn.replace(/-/g, ''))}`);

            if (queryParts.length === 0) {
                error.value = "Inserisci almeno un termine di ricerca (titolo, autore o ISBN) nel form.";
                return;
            }
            const finalQuery = queryParts.join('+');

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
                const response = await fetch(`https://www.googleapis.com/books/v1/volumes?q=${finalQuery}&maxResults=20&startIndex=${startIndex.value}`);
                if (!response.ok) throw new Error('Errore nella ricerca.');
                const data = await response.json();
                totalItems.value = data.totalItems || 0;
                const newItems = data.items || [];
                if (loadMore) {
                    results.value.push(...newItems);
                } else {
                    results.value = newItems;
                }

                startIndex.value += newItems.length;
                if (!loadMore && newItems.length === 0) error.value = "Nessun libro trovato per questa ricerca.";
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
            const isbn13 = info.industryIdentifiers?.find(id => id.type === 'ISBN_13')?.identifier;
            const isbn10 = info.industryIdentifiers?.find(id => id.type === 'ISBN_10')?.identifier;
            const selectedData = {
                title: info.title || '',
                author: (info.authors || []).join(', '),
                publisher: info.publisher || '',
                description: info.description || '',
                language: info.language || '',
                isbn: isbn13 || isbn10 || '',
                cover_url: info.imageLinks?.thumbnail?.replace('http:', 'https:') || ''
            };
            emit('book-selected', selectedData);
            close();
        };

        const close = () => emit('close');

        return { results, isLoading, isLoadingMore, error, formattedQuery, resultsContainer, search, selectBook, close, handleScroll, startIndex };
    },
    template: `
        <transition name="fade" appear>
            <div class="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" @click.self="close">
                <div class="bg-white dark:bg-slate-800 rounded-lg shadow-xl w-full max-w-3xl h-[80vh] flex flex-col">
                    <div class="p-4 border-b dark:border-slate-700 flex-shrink-0">
                        <div class="flex justify-between items-center">
                            <div>
                                <h3 class="text-xl font-bold text-slate-800 dark:text-slate-100">Risultati per:</h3>
                                <p class="text-sm text-slate-500 dark:text-slate-400 truncate">{{ formattedQuery }}</p>
                            </div>
                            <button @click="close" class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-2xl">&times;</button>
                        </div>
                    </div>
                    <div ref="resultsContainer" @scroll="handleScroll" class="overflow-y-auto p-4 flex-grow">
                        <div v-if="isLoading" class="text-center text-slate-500">Caricamento...</div>
                        <div v-else-if="error" class="text-center text-red-500">{{ error }}</div>
                        <div v-else-if="results.length > 0">
                            <div class="space-y-3">
                                <BookSearchResult v-for="(book, index) in results" :key="book.id + '-' + index" :book="book" @select="selectBook" />
                            </div>
                            <div v-if="isLoadingMore" class="text-center text-slate-500 mt-4">Caricamento altri risultati...</div>
                        </div>
                         <div v-else class="text-center text-slate-500 pt-8">Usa la barra di ricerca per trovare un libro.</div>
                    </div>
                </div>
            </div>
        </transition>
    `
};