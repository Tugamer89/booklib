import { formatISBN } from '../utils/formatters.js';

export default {
    props: ['book', 'csrfToken'],
    emits: ['edit-book', 'show-details'],
    setup() {
        return { formatISBN };
    },
    template: `
        <div class="group bg-white dark:bg-slate-800 rounded-lg shadow-lg overflow-hidden flex flex-col border border-slate-200 dark:border-slate-700">
            <div @click="$emit('show-details', book)" class="relative cursor-pointer overflow-hidden">
                <div class="transition-transform duration-300 group-hover:scale-105">
                    <img :src="book.cover_path" :alt="'Copertina di ' + book.title" class="w-full h-64 object-cover">
                    <div class="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                </div>
            </div>
            <div class="p-4 flex flex-col flex-grow">
                <h3 class="font-bold text-md truncate text-slate-800 dark:text-slate-100">{{ book.title }}</h3>
                <p class="text-slate-600 dark:text-slate-400 text-sm truncate">{{ book.author }}</p>
                <div class="mt-4 flex-grow flex items-end justify-between">
                    <span class="text-xs font-mono text-slate-400 dark:text-slate-500">{{ book.location }}</span>
                    <div class="flex items-center space-x-3 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                        <button @click.stop="$emit('edit-book', book)" class="text-indigo-500 hover:text-indigo-700" title="Modifica">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.5L14.732 3.732z"></path></svg>
                        </button>
                        <form action="/delete" method="post" @submit="confirmDelete" @click.stop>
                            <input type="hidden" name="book_id" :value="book.id">
                            <input type="hidden" name="csrf_token" :value="csrfToken">
                            <button type="submit" class="text-red-500 hover:text-red-700" title="Elimina">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    `,
    methods: {
        confirmDelete(event) {
            const userConfirmed = window.confirm(`Sei sicuro di voler eliminare "${this.book.title}"?`);
            if (!userConfirmed) {
                event.preventDefault();
            }
        }
    }
};