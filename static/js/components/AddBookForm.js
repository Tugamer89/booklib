import { ref, watch } from "vue";
import { formatISBN, liveFormatISBN } from "../utils/formatters.js";
import { Camera, Search, Loader2 } from "lucide-vue-next";
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
    components: { GoogleBooksModal, Camera, Search, Loader2 },
    setup(props, { emit }) {
        const coverPreview = ref(props.bookData.cover_url || "/static/covers/default.jpg");
        const isScanning = ref(false);
        const isSubmitting = ref(false);
        const currentFile = ref(null);
        let html5QrCode = null;

        watch(
            () => props.bookData.cover_url,
            (newUrl) => {
                if (newUrl) {
                    coverPreview.value = newUrl;
                    currentFile.value = null;
                } else if (!currentFile.value) {
                    coverPreview.value = "/static/covers/default.jpg";
                }
            }
        );

        const handleFileChange = (event) => {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();

                reader.onload = (e) => {
                    currentFile.value = file;
                    coverPreview.value = e.target.result;
                    props.bookData.cover_url = "";
                };

                reader.readAsDataURL(file);
            }
        };

        const startIsbnScanner = async () => {
            if (isScanning.value) {
                stopScanner();
                return;
            }

            // Code splitting: dynamically load html5-qrcode only when scanner is requested
            if (!window.Html5Qrcode) {
                try {
                    await new Promise((resolve, reject) => {
                        const script = document.createElement("script");
                        script.src = "https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js";
                        script.integrity =
                            "sha512-r6rDA7W6ZeQhvl8S7yRVQUKVHdexq+GAlNkNNqVC7YyIV+NwqCTJe2hDWCiffTyRNOeGEzRRJ9ifvRm/HCzGYg==";
                        script.crossOrigin = "anonymous";
                        script.onload = resolve;
                        script.onerror = reject;
                        document.head.appendChild(script);
                    });
                } catch (error) {
                    console.error("Failed to load html5-qrcode library", error);
                    return;
                }
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
            isSubmitting,
            handleFileChange,
            startIsbnScanner,
            openGoogleSearch,
            onIsbnInput,
        };
    },
    template: `
        <div class="bg-white dark:bg-slate-800 p-6 rounded-lg shadow-lg mb-8 border border-slate-200 dark:border-slate-700">
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
                <h2 class="text-2xl font-bold text-slate-800 dark:text-slate-100">Add a new book</h2>
                <button type="button" @click="openGoogleSearch" class="flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/60 transition-colors font-medium focus:outline-none focus:ring-2 focus:ring-blue-500">
                    <Search class="w-4 h-4" />
                    <span>Autofill with Google</span>
                </button>
            </div>

            <form action="/add" method="post" enctype="multipart/form-data" class="space-y-6" @submit="isSubmitting = true">
                <input type="hidden" name="csrf_token" :value="csrfToken">
                <input type="hidden" name="cover_url" v-model="bookData.cover_url">
                
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <div class="lg:col-span-2 space-y-6">
                        <fieldset class="p-4 border border-slate-200 dark:border-slate-700 rounded-lg bg-slate-50/50 dark:bg-slate-800/30">
                            <legend class="px-2 text-sm font-semibold text-slate-700 dark:text-slate-300">Essential Information</legend>
                            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-2">
                                <div class="sm:col-span-2">
                                    <label for="title" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Title <span class="text-red-500" aria-hidden="true">*</span></label>
                                    <input v-model="bookData.title" type="text" name="title" id="title" required aria-required="true" class="input-style w-full">
                                </div>
                                <div>
                                    <label for="author" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Author <span class="text-red-500" aria-hidden="true">*</span></label>
                                    <input v-model="bookData.author" type="text" name="author" id="author" required aria-required="true" class="input-style w-full">
                                </div>
                                <div>
                                    <label for="isbn" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">ISBN</label>
                                    <div class="flex gap-2">
                                        <input :value="bookData.isbn" @input="onIsbnInput" type="text" name="isbn" id="isbn" class="input-style flex-grow">
                                        <button type="button" @click="startIsbnScanner" class="px-3 py-2 rounded-md text-white transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 dark:focus:ring-offset-slate-800" :class="isScanning ? 'bg-red-500 hover:bg-red-600 focus:ring-red-500' : 'bg-teal-500 hover:bg-teal-600 focus:ring-teal-500'" title="Scan ISBN" aria-label="Scan ISBN with camera">
                                            <Camera class="w-5 h-5" />
                                        </button>
                                    </div>
                                </div>
                                <div class="sm:col-span-2">
                                    <div id="isbn-scanner-reader" class="hidden w-full rounded-md overflow-hidden border dark:border-slate-600 mt-2"></div>
                                </div>
                            </div>
                        </fieldset>

                        <fieldset class="p-4 border border-slate-200 dark:border-slate-700 rounded-lg bg-slate-50/50 dark:bg-slate-800/30">
                            <legend class="px-2 text-sm font-semibold text-slate-700 dark:text-slate-300">Details & Location</legend>
                            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-2">
                                <div>
                                    <label for="publisher" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Publisher</label>
                                    <input v-model="bookData.publisher" type="text" name="publisher" id="publisher" class="input-style w-full">
                                </div>
                                <div>
                                    <label for="language" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Language (e.g. EN)</label>
                                    <input v-model="bookData.language" type="text" name="language" id="language" maxlength="3" class="input-style w-full">
                                </div>
                                <div class="sm:col-span-2">
                                    <label for="location" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Physical Location <span class="text-red-500" aria-hidden="true">*</span></label>
                                    <input v-model="bookData.location" type="text" name="location" id="location" required aria-required="true" class="input-style w-full" pattern="[A-Z]+[0-9]+" title="Invalid format. E.g.: A5, SHELF10" oninput="this.value = this.value.toUpperCase()">
                                    <p class="text-xs text-slate-500 mt-1">Format: Letters followed by numbers (e.g. A5)</p>
                                </div>
                                <div class="sm:col-span-2">
                                    <label for="description" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Description</label>
                                    <textarea v-model="bookData.description" name="description" id="description" rows="3" class="input-style w-full resize-none"></textarea>
                                </div>
                                <div class="sm:col-span-2">
                                    <label for="personal_comment" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Personal Comment</label>
                                    <textarea v-model="bookData.personal_comment" name="personal_comment" id="personal_comment" rows="2" class="input-style w-full resize-none"></textarea>
                                </div>
                            </div>
                        </fieldset>
                    </div>

                    <div class="space-y-4">
                        <fieldset class="p-4 border border-slate-200 dark:border-slate-700 rounded-lg bg-slate-50/50 dark:bg-slate-800/30 h-full flex flex-col">
                            <legend class="px-2 text-sm font-semibold text-slate-700 dark:text-slate-300">Book Cover</legend>
                            <div class="mt-2 flex-grow flex flex-col items-center justify-center gap-4">
                                <img :src="coverPreview" alt="Cover preview" class="w-48 h-auto object-cover rounded-md border dark:border-slate-600 shadow-sm aspect-[2/3]" loading="lazy">
                                <div class="w-full">
                                    <input type="file" name="cover" id="cover-upload" @change="handleFileChange" accept="image/*" class="sr-only peer"/>
                                    <label for="cover-upload" class="cursor-pointer block w-full text-sm font-medium text-center text-indigo-700 bg-indigo-50 dark:bg-indigo-900/40 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800 rounded-md p-2 hover:bg-indigo-100 dark:hover:bg-indigo-900/60 transition-colors peer-focus-visible:ring-2 peer-focus-visible:ring-indigo-500 peer-focus-visible:ring-offset-2 dark:peer-focus-visible:ring-offset-slate-800">
                                        Upload custom cover
                                    </label>
                                </div>
                            </div>
                        </fieldset>
                    </div>
                </div>
                
                <div class="flex justify-end pt-6 mt-6 border-t border-slate-200 dark:border-slate-700">
                    <button type="submit" :disabled="isSubmitting" class="w-full sm:w-auto bg-indigo-600 text-white px-8 py-2.5 rounded-lg shadow-md hover:bg-indigo-700 transition-colors font-semibold focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:focus:ring-offset-slate-800 disabled:opacity-75 disabled:cursor-not-allowed flex items-center justify-center gap-2">
                        <Loader2 v-if="isSubmitting" class="w-5 h-5 animate-spin" />
                        {{ isSubmitting ? 'Saving...' : 'Save Book' }}
                    </button>
                </div>
            </form>
        </div>
    `,
};
