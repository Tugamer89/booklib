export default {
    name: "BookSearchResult",
    props: ["book"],
    emits: ["select"],
    setup(props) {
        const info = props.book.volumeInfo;
        const thumbnail =
            info.imageLinks?.thumbnail?.replace("http:", "https:") || "/static/covers/default.jpg";
        const title = info.title || "Title not available";
        const authors = (info.authors || []).join(", ");
        const publisher = info.publisher || "";

        let isbn = "";
        const ids = info.industryIdentifiers || [];
        if (Array.isArray(ids) && ids.length) {
            const isbn13 = ids.find(
                (i) => i.type === "ISBN_13" || i.type?.toUpperCase().includes("13")
            );
            const isbn10 = ids.find(
                (i) => i.type === "ISBN_10" || i.type?.toUpperCase().includes("10")
            );
            isbn = isbn13?.identifier || isbn10?.identifier || "";
        }

        return { thumbnail, title, authors, publisher, isbn };
    },
    template: `
        <div class="flex items-center gap-4 p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition cursor-pointer" @click="$emit('select', book)">
            <img :src="thumbnail" :alt="title" class="w-16 h-24 object-cover rounded shadow-md flex-shrink-0" loading="lazy">
            <div class="flex-grow overflow-hidden">
                <h4 class="font-bold truncate">{{ title }}</h4>
                <p class="text-sm text-slate-600 dark:text-slate-400 truncate">{{ authors }}</p>
                <p class="text-xs text-slate-500 truncate">{{ publisher }}</p>
                <p v-if="isbn" class="text-xs text-slate-500">ISBN: {{ isbn }}</p>
            </div>
            <button class="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600 transition flex-shrink-0">Select</button>
        </div>
    `,
};
