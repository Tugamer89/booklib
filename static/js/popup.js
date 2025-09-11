let deleteForm = null;

function showConfirmDialog() {
    document.getElementById("confirmOverlay").classList.remove("hidden");
    return false;
}

document.addEventListener("submit", (e) => {
    const form = e.target;
    if (form.matches("form[action$='/delete']")) {
        e.preventDefault();
        deleteForm = form;
        document.body.style.overflow = 'hidden';
        document.getElementById("confirmOverlay").classList.remove("hidden");
    }
});

document.addEventListener("DOMContentLoaded", () => {
    const cancelBtn = document.getElementById("cancelDelete");
    const confirmBtn = document.getElementById("confirmDelete");
    
    if (!cancelBtn || !confirmBtn) return;

    cancelBtn.addEventListener("click", () => {
        document.getElementById("confirmOverlay").classList.add("hidden");
        deleteForm = null;
        document.body.style.overflow = '';
    });

    confirmBtn.addEventListener("click", () => {
        if (deleteForm) {
            document.getElementById("confirmOverlay").classList.add("hidden");
            deleteForm.submit();
        }
    });
});
