import { ref } from "vue";
const isDarkPreferred =
    localStorage.theme === "dark" ||
    (!("theme" in localStorage) && globalThis.matchMedia("(prefers-color-scheme: dark)").matches);
export function useTheme() {
    const isDark = ref(isDarkPreferred) || ref(document.documentElement.classList.contains("dark"));
    const toggleTheme = () => {
        isDark.value = !isDark.value;
        if (isDark.value) {
            document.documentElement.classList.add("dark");
            localStorage.setItem("theme", "dark");
        } else {
            document.documentElement.classList.remove("dark");
            localStorage.setItem("theme", "light");
        }
    };
    return {
        toggleTheme,
        isDark,
    };
}
