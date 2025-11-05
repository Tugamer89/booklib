import { ref, computed } from 'vue';

const isDarkPreferred = localStorage.theme === 'dark' || (!('theme' in localStorage) && globalThis.matchMedia('(prefers-color-scheme: dark)').matches);
const theme = ref(isDarkPreferred ? 'dark' : 'light');


export function useTheme() {
    const toggleTheme = () => {
        const isDark = document.documentElement.classList.toggle('dark');
        const newTheme = isDark ? 'dark' : 'light';
        theme.value = newTheme;
        localStorage.setItem('theme', newTheme);
    };

    const themeIcon = computed(() => theme.value === 'light' ? '🌙' : '☀️');

    return {
        theme,
        toggleTheme,
        themeIcon,
    };
}