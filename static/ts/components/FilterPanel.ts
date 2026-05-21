import { computed } from "vue";

export default {
    name: "FilterPanel",
    props: {
        modelValue: {
            type: Object,
            required: true,
        },
    },
    emits: ["update:modelValue", "applyNow", "resetNow"],
    setup(props, { emit }) {
        const filters = computed({
            get: () => props.modelValue,
            set: (newValue) => {
                emit("update:modelValue", newValue);
            },
        });

        const reset = () => {
            emit("resetNow");
        };

        const apply = () => {
            emit("applyNow");
        };

        return { filters, reset, apply };
    },
    template: `
        <div class="mb-8 p-6 bg-white dark:bg-slate-800 rounded-lg shadow-md border border-slate-200 dark:border-slate-700">
            <form @submit.prevent="apply">
                <div class="border-b border-slate-200 dark:border-slate-700 pb-6 mb-6">
                    <h3 class="text-lg font-semibold text-slate-700 dark:text-slate-200">Filter by</h3>
                    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-4">
                        <div>
                            <label for="filter-title" class="block text-sm font-medium text-slate-600 dark:text-slate-300">Title</label>
                            <input v-model="filters.title" type="text" id="filter-title" class="mt-1 input-style">
                        </div>
                        <div>
                            <label for="filter-author" class="block text-sm font-medium text-slate-600 dark:text-slate-300">Author</label>
                            <input v-model="filters.author" type="text" id="filter-author" class="mt-1 input-style">
                        </div>
                        <div>
                            <label for="filter-publisher" class="block text-sm font-medium text-slate-600 dark:text-slate-300">Publisher</label>
                            <input v-model="filters.publisher" type="text" id="filter-publisher" class="mt-1 input-style">
                        </div>
                        <div>
                            <label for="filter-location" class="block text-sm font-medium text-slate-600 dark:text-slate-300">Location</label>
                            <input v-model="filters.location" type="text" id="filter-location" class="mt-1 input-style">
                        </div>
                    </div>
                </div>

                <div>
                    <h3 class="text-lg font-semibold text-slate-700 dark:text-slate-200">Sort by</h3>
                    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-4">
                        <div class="sm:col-span-2">
                            <label for="sort-by" class="block text-sm font-medium text-slate-600 dark:text-slate-300">Criteria</label>
                            <select v-model="filters.sort_by" id="sort-by" class="mt-1 input-style">
                                <option value="id">Date Added</option>
                                <option value="title">Title</option>
                                <option value="author">Author</option>
                                <option value="location">Location</option>
                            </select>
                        </div>
                        <div>
                            <label for="sort-order" class="block text-sm font-medium text-slate-600 dark:text-slate-300">Direction</label>
                            <select v-model="filters.sort_order" id="sort-order" class="mt-1 input-style">
                                <option value="asc">Ascending</option>
                                <option value="desc">Descending</option>
                            </select>
                        </div>
                    </div>
                </div>

                <div class="flex justify-end space-x-3 mt-6 border-t border-slate-200 dark:border-slate-700 pt-4">
                     <button @click="reset" type="button" class="bg-slate-200 dark:bg-slate-600 text-slate-700 dark:text-slate-200 px-4 py-2 rounded-md hover:bg-slate-300 dark:hover:bg-slate-500 transition">Reset</button>
                     <button type="submit" class="bg-indigo-600 text-white px-4 py-2 rounded-md shadow hover:bg-indigo-700 transition">Apply</button>
                </div>
            </form>
        </div>
    `,
};
