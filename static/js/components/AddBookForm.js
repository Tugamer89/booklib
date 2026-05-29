import { ref, watch } from "vue";
import { formatISBN, liveFormatISBN } from "../utils/formatters.js";
import { Camera, Search } from "lucide-vue-next";
import GoogleBooksModal from "./GoogleBooksModal.js";

export default {
    name: "AddBookForm",
    props: {
        bookData: {
            type: Object,
            required: true,
        },
        csrfToken: String,
    },
    emits: ["open-google-search"],
    components: { GoogleBooksModal, Camera, Search },
    setup(props, { emit }) {
        const coverPreview = ref(props.bookData.cover_url || "/static/covers/default.jpg");
        const isScanning = ref(false);
        let html5QrCode = null;

        watch(
            () => props.bookData.cover_url,
            (newUrl) => {
                if (newUrl) {
                    coverPreview.value = newUrl;
                } else if (!file) {
                    coverPreview.value = "/static/covers/default.jpg";
                }
            }
        );

        const handleFileChange = (event) => {
            const file = event.target.files[0];
            if (file) {
                coverPreview.value = URL.createObjectURL(file);
                props.bookData.cover_url = "";
            }
        };

        const startIsbnScanner = () => {
            if (isScanning.value) {
                stopScanner();
                return;
            }
            isScanning.value = true;
            const readerElement = document.getElementById("isbn-scanner-reader");
            readerElement.classList.remove("hidden");

            html5QrCode = new Html5Qrcode("isbn-scanner-reader");
            html5QrCode
                .start(
                    { facingMode: "environment" },
                    { fps: 10, qrbox: { width: 250, height: 150 } },
                    (decodedText) => {
                        props.bookData.isbn = formatISBN(decodedText);
                        stopScanner();
                    },
                    (errorMessage) => {
                        /* ignore errors */
                    }
                )
                .catch((err) => {
                    console.error(
                        "Error starting camera. Make sure you have granted the necessary permissions."
                    );
                    stopScanner();
                });
        };

        const stopScanner = () => {
            if (html5QrCode?.isScanning) {
                html5QrCode
                    .stop()
                    .then(() => {
                        const readerElement = document.getElementById("isbn-scanner-reader");
                        if (readerElement) readerElement.classList.add("hidden");
                        isScanning.value = false;
                    })
                    .catch((err) => {
                        console.error("Error stopping the scanner.", err);
                        isScanning.value = false;
                    });
            } else {
                isScanning.value = false;
                const readerElement = document.getElementById("isbn-scanner-reader");
                if (readerElement) readerElement.classList.add("hidden");
            }
        };

        const onIsbnInput = (event) => {
            props.bookData.isbn = liveFormatISBN(event.target.value);
        };

        const openGoogleSearch = () => {
            emit("open-google-search", props.bookData);
        };

        return {
            coverPreview,
            isScanning,
            handleFileChange,
            startIsbnScanner,
            openGoogleSearch,
            onIsbnInput,
        };
    },
    template: `
        <div class="bg-white dark:bg-slate-800 p-6 rounded-lg shadow-lg mb-8 border border-slate-200 dark:border-slate-700">
            <h2 class="text-2xl font-bold mb-6 text-slate-800 dark:text-slate-100">Add a new book</h2>

            <form action="/add" method="post" enctype="multipart/form-data">
                <input type="hidden" name="csrf_token" :value="csrfToken">
                <input type="hidden" name="cover_url" v-model="bookData.cover_url">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    
                    <div class="md:col-span-2 grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div class="sm:col-span-2">
                            <label for="title" class="block text-sm font-medium text-slate-600 dark:text-slate-300">Title *</label>
                            <input v-model="bookData.title" type="text" name="title" id="title" required class="mt-1 input-style">
                        </div>
                        <div>
                            <label for="author" class="block text-sm font-medium text-slate-600 dark:text-slate-300">Author *</label>
                            <input v-model="bookData.author" type="text" name="author" id="author" required class="mt-1 input-style">
                        </div>
                        <div>
                            <label for="publisher" class="block text-sm font-medium text-slate-600 dark:text-slate-300">Publisher</label>
                            <input v-model="bookData.publisher" type="text" name="publisher" id="publisher" class="mt-1 input-style">
                        </div>
                        <div class="sm:col-span-2">
                            <label for="isbn" class="block text-sm font-medium text-slate-600 dark:text-slate-300">ISBN</label>
                            <div class="flex gap-2 mt-1">
                                <input :value="bookData.isbn" @input="onIsbnInput" type="text" name="isbn" id="isbn" class="input-style flex-grow">
                                <button type="button" @click="startIsbnScanner" class="px-3 py-2 rounded-md text-white transition-colors" :class="isScanning ? 'bg-red-500 hover:bg-red-600' : 'bg-teal-500 hover:bg-teal-600'" title="Scan ISBN" aria-label="Scan ISBN with camera">
                                    <Camera class="w-5 h-5" />
                                </button>
                            </div>
                            <div id="isbn-scanner-reader" class="mt-2 hidden w-full rounded-md overflow-hidden border dark:border-slate-600"></div>
                        </div>
                        <div>
                            <label for="location" class="block text-sm font-medium text-slate-600 dark:text-slate-300">Location *</label>
                            <input v-model="bookData.location" type="text" name="location" id="location" required class="mt-1 input-style" pattern="[A-Z]+[0-9]+" title="Invalid format. E.g.: A5, SHELF10" oninput="this.value = this.value.toUpperCase()">
                        </div>
                        <div>
                            <label for="language" class="block text-sm font-medium text-slate-600 dark:text-slate-300">Language (e.g. EN)</label>
                            <input v-model="bookData.language" type="text" name="language" id="language" maxlength="3" class="mt-1 input-style">
                        </div>
                        <div class="sm:col-span-2">
                            <label for="description" class="block text-sm font-medium text-slate-600 dark:text-slate-300">Description</label>
                            <textarea v-model="bookData.description" name="description" id="description" rows="3" class="mt-1 input-style resize-none"></textarea>
                        </div>
                        <div class="sm:col-span-2">
                            <label for="personal_comment" class="block text-sm font-medium text-slate-600 dark:text-slate-300">Personal Comment</label>
                            <textarea v-model="bookData.personal_comment" name="personal_comment" id="personal_comment" rows="3" class="mt-1 input-style resize-none"></textarea>
                        </div>
                    </div>

                    <div class="space-y-2">
                            <label class="block text-sm font-medium text-slate-600 dark:text-slate-300">Cover Preview</label>
                            <img :src="coverPreview" alt="Cover preview" class="w-full h-auto object-contain rounded-md border dark:border-slate-600 aspect-[3/4]" loading="lazy">
                            <input type="file" name="cover" id="cover-upload" @change="handleFileChange" accept="image/*" class="sr-only peer"/>
                            <label for="cover-upload" class="cursor-pointer mt-1 block w-full text-sm text-center text-slate-500 bg-slate-50 dark:bg-slate-700 dark:text-slate-300 border rounded-md p-2 hover:bg-slate-100 dark:hover:bg-slate-600 transition peer-focus-visible:ring-2 peer-focus-visible:ring-indigo-500 peer-focus-visible:ring-offset-2 dark:peer-focus-visible:ring-offset-slate-800">
                            Upload a file
                            </label>
                    </div>
                </div>
                
                <div class="mt-8 flex flex-col-reverse sm:flex-row justify-between items-center gap-4 border-t border-slate-200 dark:border-slate-700 pt-6">
                    <button type="button" @click="openGoogleSearch" class="w-full sm:w-auto flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg shadow-md hover:bg-blue-700 transition-colors font-semibold">
                        <Search class="w-5 h-5" />
                        <span>Fill with Google Books</span>
                    </button>
                    <button type="submit" class="w-full sm:w-auto bg-indigo-600 text-white px-6 py-2 rounded-lg shadow-md hover:bg-indigo-700 transition-colors font-semibold">
                        Add Book
                    </button>
                </div>
            </form>
        </div>
    `,
};
