export default {
    name: 'BookSearchResult',
    props: ['book'],
    emits: ['select'],
    setup(props) {
        const info = props.book.volumeInfo;
        const thumbnail = info.imageLinks?.thumbnail?.replace('http:', 'https:') || '/static/covers/default.jpg';
        const title = info.title || 'Titolo non disponibile';
        const authors = (info.authors || []).join(', ');
        const publisher = info.publisher || '';
        return { thumbnail, title, authors, publisher };
    },
    template: `
        <div class="flex items-center gap-4 p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition cursor-pointer" @click="$emit('select', book)">
            <img :src="thumbnail" :alt="title" class="w-16 h-24 object-cover rounded shadow-md flex-shrink-0">
            <div class="flex-grow overflow-hidden">
                <h4 class="font-bold truncate">{{ title }}</h4>
                <p class="text-sm text-slate-600 dark:text-slate-400 truncate">{{ authors }}</p>
                <p class="text-xs text-slate-500">{{ publisher }}</p>
            </div>
            <button class="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600 transition flex-shrink-0">Seleziona</button>
        </div>
    `
};