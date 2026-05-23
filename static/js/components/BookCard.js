import { formatISBN } from "../utils/formatters.js";
import { Pencil, Trash2 } from "lucide-vue-next";

export default {
    props: ["book", "csrfToken"],
    emits: ["edit-book", "show-details"],
    components: { Pencil, Trash2 },
    setup() {
        return { formatISBN };
    },
    template: `
        <div class="group bg-white dark:bg-slate-800 rounded-lg shadow-lg overflow-hidden flex flex-col border border-slate-200 dark:border-slate-700">
            <div @click="$emit('show-details', book)" @keydown.enter.prevent="$emit('show-details', book)" @keydown.space.prevent="$emit('show-details', book)" role="button" tabindex="0" class="relative cursor-pointer overflow-hidden focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-inset" aria-label="View book details">
                <div class="transition-transform duration-300 group-hover:scale-105">
                    <img :src="book.cover_path" :alt="'Cover of ' + book.title" class="w-full h-64 object-cover defer">
                    <div class="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                </div>
            </div>
            <div class="p-4 flex flex-col flex-grow">
                <h3 class="font-bold text-md truncate text-slate-800 dark:text-slate-100">{{ book.title }}</h3>
                <p class="text-slate-600 dark:text-slate-400 text-sm truncate">{{ book.author }}</p>
                <div class="mt-4 flex-grow flex items-end justify-between">
                    <span class="text-xs font-mono text-slate-400 dark:text-slate-500">{{ book.location }}</span>
                    <div class="flex items-center space-x-3 opacity-0 group-hover:opacity-100 has-[:focus-visible]:opacity-100 transition-opacity duration-200">
                        <button @click.stop="$emit('edit-book', book)" class="flex items-center justify-center rounded p-1 text-indigo-500 hover:text-indigo-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500" title="Edit" aria-label="Edit book">
                            <Pencil class="w-5 h-5" />
                        </button>
                        
                        <form action="/delete" method="post" @submit="confirmDelete" @click.stop class="flex items-center m-0">
                            <input type="hidden" name="book_id" :value="book.id">
                            <input type="hidden" name="csrf_token" :value="csrfToken">
                            <button type="submit" class="flex items-center justify-center rounded p-1 text-red-500 hover:text-red-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-red-500" title="Delete" aria-label="Delete book">
                                <Trash2 class="w-5 h-5" />
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    `,
    methods: {
        confirmDelete(event) {
            const userConfirmed = globalThis.confirm(
                `Are you sure you want to delete "${this.book.title}"?`
            );
            if (!userConfirmed) {
                event.preventDefault();
            }
        },
    },
};
