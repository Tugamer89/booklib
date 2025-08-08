let deleteForm = null;

function showConfirmDialog() {
    document.getElementById("confirmOverlay").classList.remove("hidden");
    return false;
}

document.addEventListener("DOMContentLoaded", () => {
    const cancelBtn = document.getElementById("cancelDelete");
    const confirmBtn = document.getElementById("confirmDelete");
    
    if (!cancelBtn || !confirmBtn) return;

    document.querySelectorAll("form[action='/delete']").forEach(form => {
        form.addEventListener("submit", (e) => {
            e.preventDefault();
            deleteForm = form;
            showConfirmDialog();
        });
    });

    cancelBtn.addEventListener("click", () => {
        document.getElementById("confirmOverlay").classList.add("hidden");
        deleteForm = null;
    });

    confirmBtn.addEventListener("click", () => {
        if (deleteForm) {
            document.getElementById("confirmOverlay").classList.add("hidden");
            deleteForm.submit();
    }
    });
});
