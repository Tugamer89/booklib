document.addEventListener("DOMContentLoaded", () => {
    const html = document.documentElement;
    const themeToggle = document.getElementById("theme-toggle");
    const themeLabel = document.getElementById("theme-label");

    const savedTheme = localStorage.getItem("theme");
    if (savedTheme) {
        html.setAttribute("data-theme", savedTheme);
        updateLabel(savedTheme);
    } else {
        const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
        const initialTheme = prefersDark ? "dark" : "light";
        html.setAttribute("data-theme", initialTheme);
        updateLabel(initialTheme);
    }

    themeToggle.addEventListener("click", () => {
        const current = html.getAttribute("data-theme");
        const next = current === "light" ? "dark" : "light";
        html.setAttribute("data-theme", next);
        localStorage.setItem("theme", next);
        updateLabel(next);
    });

    function updateLabel(theme) {
        if (theme === "dark") {
            themeLabel.textContent = "🌙 Scuro";
        } else {
            themeLabel.textContent = "🌞 Chiaro";
        }
    }
});
