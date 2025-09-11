let html5QrCode;
let isScanning = false;

function toggleScanner() {
    const button = document.getElementById("toggle-scanner");
    const container = document.getElementById("scanner-container");
    const loadingOverlay = document.getElementById("loading-overlay");

    if (!document.getElementById("reader")) return;

    if (!isScanning) {
        container.classList.remove("hidden");
        loadingOverlay.classList.remove("hidden");

        button.textContent = "❌ Chiudi scansione";
        button.classList.remove("bg-green-600", "hover:bg-green-700");
        button.classList.add("bg-red-600", "hover:bg-red-700");

        html5QrCode = new Html5Qrcode("reader");
        html5QrCode.start(
            { facingMode: "environment" },
            {
                fps: 30,
                qrbox: 250,
                formatsToSupport: [
                    Html5QrcodeSupportedFormats.EAN_13,
                    Html5QrcodeSupportedFormats.EAN_8,
                    Html5QrcodeSupportedFormats.CODE_128
                ]
            },
            (decodedText) => {
                const input = document.getElementById("isbnAdd");
                if (input) input.value = formatISBN(decodedText);
                stopScanner();
            },
            (error) => {
                
            }
        ).then(() => {
            loadingOverlay.classList.add("hidden");
        }).catch(err => {
            alert("Errore scanner: " + err);
            stopScanner();
        });

        isScanning = true;
    } else {
        stopScanner();
    }
}

function stopScanner() {
    const button = document.getElementById("toggle-scanner");
    const container = document.getElementById("scanner-container");
    const loadingOverlay = document.getElementById("loading-overlay");

    if (html5QrCode) {
        html5QrCode.stop().then(() => {
            html5QrCode.clear();
            html5QrCode = null;
        });
    }

    container.classList.add("hidden");
    loadingOverlay.classList.add("hidden");

    button.textContent = "📷 Avvia scansione ISBN";
    button.classList.remove("bg-red-600", "hover:bg-red-700");
    button.classList.add("bg-green-600", "hover:bg-green-700");

    isScanning = false;
}

window.toggleScanner = toggleScanner;
