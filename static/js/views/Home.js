import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
import { useTheme } from '../utils/theme.js';
import { useBodyScrollLock } from '../utils/useBodyScrollLock.js';
import { api } from '../services/api.js';
import { formatISBN } from '../utils/formatters.js';

import Navbar from '../components/Navbar.js';
import BookCard from '../components/BookCard.js';
import AddBookForm from '../components/AddBookForm.js';
import EditBookModal from '../components/EditBookModal.js';
import DetailModal from '../components/DetailModal.js';
import FilterPanel from '../components/FilterPanel.js';
import GoogleBooksModal from '../components/GoogleBooksModal.js';

export default {
    components: {
        Navbar, BookCard, AddBookForm, EditBookModal, DetailModal, FilterPanel, GoogleBooksModal
    },
    setup() {
        const books = ref([]);
        const isLoading = ref(false);
        const hasMore = ref(true);
        const currentOffset = ref(0);
        const fetchError = ref(null);

        const currentFilters = ref({
            title: '', author: '', publisher: '', location: '',
            sort_by: 'id', sort_order: 'asc'
        });

        const showAddForm = ref(localStorage.getItem('showAddForm') === 'true');
        const showFilters = ref(localStorage.getItem('showFilters') === 'true');
        const showScrollToTop = ref(false);

        const selectedBookForEdit = ref(null);
        const selectedBookForDetail = ref(null);
        const showGoogleBooksModal = ref(false);
        const googleSearchTerms = ref({});
        const newBookData = ref({
            title: '', author: '', isbn: '', publisher: '',
            location: '', language: '', description: '', personal_comment: '',
            cover_url: ''
        });

        const userData = JSON.parse(document.getElementById('user-data').textContent);
        const csrfToken = ref(JSON.parse(document.getElementById('csrf-token').textContent));
        const username = ref(userData.username);
        const isAdmin = ref(userData.is_admin);

        const { theme, toggleTheme } = useTheme();
        const isAnyModalOpen = computed(() =>
            !!selectedBookForEdit.value ||
            !!selectedBookForDetail.value ||
            showGoogleBooksModal.value
        );
        useBodyScrollLock(isAnyModalOpen);



        let debounceTimer = null;
        let lastAppliedFilters = JSON.stringify(currentFilters.value);

        const fetchBooks = async (reset = false) => {
            if (isLoading.value || (!reset && !hasMore.value)) return;
            isLoading.value = true;
            if (reset) {
                currentOffset.value = 0;
                books.value = [];
                hasMore.value = true;
            }
            const params = { ...currentFilters.value, offset: currentOffset.value, limit: 20 };
            try {
                fetchError.value = null;
                const data = await api.getBooks(params);
                books.value.push(...data.books);
                hasMore.value = data.has_more;
                currentOffset.value += data.books.length;
            } catch (error) {
                fetchError.value = "Impossibile caricare i libri. Riprova più tardi.";
                console.error(error);
            } finally {
                isLoading.value = false;
            }
        };

        const applyFiltersAndUrl = () => {
            const currentFiltersString = JSON.stringify(currentFilters.value);
            if (lastAppliedFilters === currentFiltersString) return;

            fetchBooks(true);
            lastAppliedFilters = currentFiltersString;

            const urlParams = new URLSearchParams();
            for (const [key, value] of Object.entries(currentFilters.value)) {
                if (value && String(value).trim() !== '') {
                    if (key === 'sort_by' && value === 'id') continue;
                    if (key === 'sort_order' && value === 'asc') continue;
                    urlParams.append(key, value);
                }
            }
            const queryString = urlParams.toString();
            const newUrl = queryString ? `${window.location.pathname}?${queryString}` : window.location.pathname;
            window.history.pushState({ path: newUrl }, '', newUrl);
        };

        watch(currentFilters, () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(applyFiltersAndUrl, 500);
        }, { deep: true });



        let scrollDebounceTimer = null;
        let resizeDebounceTimer = null;

        const onScroll = () => {
            const scrollableHeight = document.documentElement.scrollHeight - window.innerHeight;
            const scrollPosition = window.scrollY;
            
            if (scrollableHeight > 0 && (scrollPosition / scrollableHeight) > 0.85) {
                fetchBooks();
            }
            
            showScrollToTop.value = window.scrollY > 400;
        };

        const onResize = () => {
            showScrollToTop.value = window.scrollY > 400;
        };

        const handleScroll = () => {
            clearTimeout(scrollDebounceTimer);
            scrollDebounceTimer = setTimeout(onScroll, 100); 
        };
        
        const handleResize = () => {
            clearTimeout(resizeDebounceTimer);
            resizeDebounceTimer = setTimeout(onResize, 100);
        };

        const scrollToTop = () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        };

        const applyFiltersNow = () => {
            clearTimeout(debounceTimer);
            applyFiltersAndUrl();
        };
        const resetFiltersNow = () => {
            currentFilters.value = {
                title: '', author: '', publisher: '', location: '',
                sort_by: 'id', sort_order: 'asc'
            };
            applyFiltersNow();
        };
        const openEditModal = (book) => { selectedBookForEdit.value = book; };
        const openDetailModal = (book) => { selectedBookForDetail.value = book; };
        const openGoogleSearch = (searchTerms) => {
            googleSearchTerms.value = searchTerms;
            showGoogleBooksModal.value = true;
        };
        const handleBookSelected = (selectedBook) => {
            newBookData.value.title = selectedBook.title;
            newBookData.value.author = selectedBook.author;
            newBookData.value.publisher = selectedBook.publisher;
            newBookData.value.isbn = formatISBN(selectedBook.isbn);
            newBookData.value.description = selectedBook.description;
            newBookData.value.language = selectedBook.language;
            newBookData.value.cover_url = selectedBook.cover_url;
        };
        const resetNewBookData = () => {
            newBookData.value = {
                title: '', author: '', isbn: '', publisher: '',
                location: '', language: '', description: '', personal_comment: '',
                cover_url: ''
            };
        };
        watch(showAddForm, (isShown) => {
            if (!isShown) {
                resetNewBookData();
            }
            localStorage.setItem('showAddForm', isShown);
        });

        watch(showFilters, (isShown) => {
            localStorage.setItem('showFilters', isShown);
        });

        onMounted(() => {
            window.scrollTo(0, 0);

            const urlParams = new URLSearchParams(window.location.search);
            const filtersFromUrl = {};
            for (const [key, value] of urlParams.entries()) {
                filtersFromUrl[key] = value;
            }
            currentFilters.value = { ...currentFilters.value, ...filtersFromUrl };

            lastAppliedFilters = JSON.stringify(currentFilters.value);

            fetchBooks();
            
            window.addEventListener('scroll', handleScroll);
            window.addEventListener('resize', handleResize);
        });

        onUnmounted(() => {
            window.removeEventListener('scroll', handleScroll);
            window.removeEventListener('resize', handleResize);
        });


        return {
            books, isLoading, fetchError, currentFilters,
            showAddForm, showFilters, showScrollToTop,
            selectedBookForEdit, selectedBookForDetail, showGoogleBooksModal,
            newBookData, googleSearchTerms,
            username, isAdmin, theme,
            isAnyModalOpen,
            csrfToken,

            toggleTheme,
            scrollToTop,
            applyFiltersNow,
            resetFiltersNow,
            openEditModal,
            openDetailModal,
            openGoogleSearch,
            handleBookSelected
        };
    },
    template: `
        <Navbar :is-admin="isAdmin" :username="username" :theme="theme" @toggle-theme="toggleTheme" />

        <main class="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div v-if="fetchError" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
                <strong class="font-bold">Oops!</strong>
                <span class="block sm:inline">{{ fetchError }}</span>
            </div>

            <div class="flex flex-wrap justify-between items-center gap-4 mb-8">
                 <h1 class="text-3xl font-bold text-slate-800 dark:text-slate-100">La mia Libreria</h1>
                 <div class="flex items-center gap-2">
                     <button @click="showFilters = !showFilters" class="bg-slate-600 text-white px-4 py-2 rounded-lg shadow-md hover:bg-slate-700 transition-colors">Filtra & Ordina</button>
                     <button @click="showAddForm = !showAddForm" class="bg-indigo-600 text-white px-4 py-2 rounded-lg shadow-md hover:bg-indigo-700 transition-colors">
                        {{ showAddForm ? 'Annulla' : 'Aggiungi Libro' }}
                    </button>
                 </div>
            </div>

            <transition name="fade">
                <FilterPanel
                    v-if="showFilters"
                    v-model="currentFilters"
                    @apply-now="applyFiltersNow"
                    @reset-now="resetFiltersNow"
                />
            </transition>
            <transition name="fade">
                <AddBookForm
                    v-if="showAddForm"
                    :book-data="newBookData"
                    @open-google-search="openGoogleSearch"
                    id="add-book-form-component"
                    :csrf-token="csrfToken"
                />
            </transition>

            <div v-if="isLoading && books.length === 0" class="text-center py-12 text-slate-500 dark:text-slate-400">
                <p>Caricamento in corso...</p>
            </div>
             <div v-else-if="books.length === 0" class="text-center py-12 text-slate-500 dark:text-slate-400">
                <p>Nessun libro trovato. Prova a cambiare i filtri o aggiungine uno nuovo!</p>
            </div>
            <div v-else class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                <BookCard
                    v-for="book in books"
                    :key="book.id"
                    :book="book"
                    @edit-book="openEditModal"
                    @show-details="openDetailModal"
                    :csrf-token="csrfToken"
                />
            </div>
             <div v-if="isLoading && books.length > 0" class="text-center py-8 text-slate-500 dark:text-slate-400">
                <p>Caricamento altri libri...</p>
            </div>
        </main>

        <EditBookModal
            v-if="selectedBookForEdit"
            :book="selectedBookForEdit"
            @close="selectedBookForEdit = null"
            :csrf-token="csrfToken"
        />
        <DetailModal v-if="selectedBookForDetail" :book="selectedBookForDetail" @close="selectedBookForDetail = null" />
        <GoogleBooksModal
            v-if="showGoogleBooksModal"
            :isVisible="showGoogleBooksModal"
            :initial-search-terms="googleSearchTerms"
            @close="showGoogleBooksModal = false"
            @book-selected="handleBookSelected"
            :csrf-token="csrfToken"
        />

        <transition name="slide-fade">
            <button
                v-if="showScrollToTop"
                @click="scrollToTop"
                class="fixed bottom-8 right-8 z-30 w-12 h-12 rounded-full bg-indigo-600 text-white flex items-center justify-center shadow-lg hover:bg-indigo-700 transition-all"
                :class="{ 'opacity-50 cursor-not-allowed': isAnyModalOpen }"
                :disabled="isAnyModalOpen"
                aria-label="Torna in cima"
            >
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
                </svg>
            </button>
        </transition>
    `
};