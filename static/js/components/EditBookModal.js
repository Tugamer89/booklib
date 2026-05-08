import { formatISBN } from "../utils/formatters.js";

export default {
    props: ["book", "csrfToken"],
    emits: ["close"],
    setup(props, { emit }) {
        const close = () => emit("close");
        const locationPattern = "[A-Z]+[0-9]+";
        return { close, formatISBN, locationPattern };
    },
    template: `
        <transition name="fade" appear>
            <div class="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
                <div v-click-outside="close" class="bg-white dark:bg-slate-800 rounded-lg shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
                    <form action="/edit" method="post" enctype="multipart/form-data" class="p-6">
                        <div class="flex justify-between items-center mb-6">
                            <h3 class="text-xl font-bold text-slate-800 dark:text-slate-100">Modifica Libro</h3>
                            <button @click.prevent="close" class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-2xl">&times;</button>
                        </div>
                        
                        <input type="hidden" name="book_id" :value="book.id">
                        <input type="hidden" name="csrf_token" :value="csrfToken">
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-left">
                            <div>
                                <label class="block text-sm font-medium text-slate-600 dark:text-slate-300">Titolo *</label>
                                <input type="text" name="title" :value="book.title" required class="mt-1 input-style">
                            </div>
                             <div>
                                <label class="block text-sm font-medium text-slate-600 dark:text-slate-300">Autore *</label>
                                <input type="text" name="author" :value="book.author" required class="mt-1 input-style">
                            </div>
                             <div>
                                <label class="block text-sm font-medium text-slate-600 dark:text-slate-300">ISBN</label>
                                <input type="text" name="isbn" :value="book.isbn" class="mt-1 input-style">
                            </div>
                             <div>
                                <label class="block text-sm font-medium text-slate-600 dark:text-slate-300">Casa editrice</label>
                                <input type="text" name="publisher" :value="book.publisher" class="mt-1 input-style">
                            </div>
                             <div>
                                <label class="block text-sm font-medium text-slate-600 dark:text-slate-300">Posizione *</label>
                                <input type="text" name="location" :value="book.location" required class="mt-1 input-style" :pattern="locationPattern" title="Es: A5, LIBRERIA10" oninput="this.value = this.value.toUpperCase()">
                            </div>
                             <div>
                                <label class="block text-sm font-medium text-slate-600 dark:text-slate-300">Lingua</label>
                                <input type="text" name="language" :value="book.language" class="mt-1 input-style">
                            </div>
                            <div class="md:col-span-2">
                                <label class="block text-sm font-medium text-slate-600 dark:text-slate-300">Descrizione</label>
                                <textarea name="description" rows="2" class="mt-1 input-style">{{ book.description }}</textarea>
                            </div>
                            <div class="md:col-span-2">
                                <label class="block text-sm font-medium text-slate-600 dark:text-slate-300">Commento personale</label>
                                <textarea name="personal_comment" rows="2" class="mt-1 input-style">{{ book.personal_comment }}</textarea>
                            </div>
                             <div class="md:col-span-2">
                                <label class="block text-sm font-medium text-slate-600 dark:text-slate-300">Sostituisci Copertina</label>
                                <input type="file" name="cover" accept="image/*" class="mt-1 block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 dark:file:bg-slate-700 file:text-indigo-700 dark:file:text-indigo-300 hover:file:bg-indigo-100 dark:hover:file:bg-slate-600"/>
                            </div>
                        </div>

                        <div class="flex justify-end space-x-3 mt-6 border-t border-slate-200 dark:border-slate-700 pt-4">
                            <button type="button" @click="close" class="bg-slate-200 dark:bg-slate-600 px-4 py-2 rounded-md hover:bg-slate-300 dark:hover:bg-slate-500 transition">Annulla</button>
                            <button type="submit" class="bg-indigo-600 text-white px-4 py-2 rounded-md shadow hover:bg-indigo-700 transition">Salva Modifiche</button>
                        </div>
                    </form>
                </div>
            </div>
        </transition>
    `,
};
