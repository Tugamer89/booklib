import { formatISBN } from "../utils/formatters.js";
import { X } from "lucide-vue-next";

export default {
    props: ["book"],
    emits: ["close"],
    components: { X },
    setup(props, { emit }) {
        const close = () => emit("close");
        return { close, formatISBN };
    },
    template: `
        <transition name="fade" appear>
            <div class="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" @click.self="close">

                <div class="bg-white dark:bg-slate-800 rounded-lg shadow-xl w-full max-w-3xl max-h-[90vh] flex flex-col overflow-hidden">

                    <div class="p-6 pb-4 flex-shrink-0 flex justify-between items-start gap-4">
                        <div class="flex-grow">
                            <h2 class="text-2xl font-bold text-slate-800 dark:text-slate-100 mb-1">{{ book.title }}</h2>
                            <p class="text-lg text-slate-500 dark:text-slate-400">{{ book.author }}</p>
                        </div>
                        <button @click="close" class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-3xl -mt-2 -mr-2 flex-shrink-0">
                            <X class="w-6 h-6" />
                        </button>
                    </div>

                    <div class="flex-grow flex flex-col md:flex-row gap-6 px-6 overflow-y-auto">
                        <div class="w-full md:w-1/3 flex-shrink-0">
                            <img :src="book.cover_path" :alt="'Cover of ' + book.title" class="w-full h-auto object-contain rounded-lg shadow-md sticky top-0">
                        </div>

                        <div class="w-full md:w-2/3 text-sm text-left">
                            <div class="grid grid-cols-1 sm:grid-cols-3 gap-x-4 gap-y-3 border-t border-slate-200 dark:border-slate-700 pt-4">
                                <strong class="text-slate-500 dark:text-slate-400">Publisher:</strong>
                                <span class="sm:col-span-2">{{ book.publisher || 'N/A' }}</span>

                                <strong class="text-slate-500 dark:text-slate-400">ISBN:</strong>
                                <span class="sm:col-span-2 font-mono">{{ formatISBN(book.isbn) }}</span>

                                <strong class="text-slate-500 dark:text-slate-400">Location:</strong>
                                <span class="sm:col-span-2 font-mono">{{ book.location }}</span>

                                <strong class="text-slate-500 dark:text-slate-400">Language:</strong>
                                <span class="sm:col-span-2">{{ book.language || 'N/A' }}</span>
                            </div>

                            <div class="mt-4" v-if="book.description">
                                <h4 class="font-semibold border-t border-slate-200 dark:border-slate-700 pt-3 mt-3">Description</h4>
                                <p class="mt-1 text-slate-600 dark:text-slate-300 whitespace-pre-wrap">{{ book.description }}</p>
                            </div>
                             <div class="mt-4" v-if="book.personal_comment">
                                <h4 class="font-semibold border-t border-slate-200 dark:border-slate-700 pt-3 mt-3">Personal comment</h4>
                                <p class="mt-1 text-slate-600 dark:text-slate-300 italic whitespace-pre-wrap">{{ book.personal_comment }}</p>
                            </div>
                        </div>
                    </div>

                    <div class="p-3 flex-shrink-0"></div>

                </div>
            </div>
        </transition>
    `,
};
