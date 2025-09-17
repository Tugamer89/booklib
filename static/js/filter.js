document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("filterFormElement");
    if (!form) return;

    form.addEventListener("submit", (event) => {
        event.preventDefault();

        const url = new URL(window.location.href);
        const params = new URLSearchParams(url.search);

        const formData = new FormData(form);
        for (const [key, value] of formData.entries()) {
            if (value.trim() !== "") {
                params.set(key, value.trim());
            } else {
                params.delete(key);
            }
        }

        window.location.href = `${form.action}?${params.toString()}`;
    });
});
