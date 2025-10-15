import { watch, onUnmounted } from 'vue';

const lockClass = 'overflow-hidden';

export function useBodyScrollLock(isLocked) {
    watch(isLocked, (newVal) => {
        if (newVal) {
            document.body.classList.add(lockClass);
            document.documentElement.classList.add(lockClass); // Aggiungi questo
        } else {
            document.body.classList.remove(lockClass);
            document.documentElement.classList.remove(lockClass); // E questo
        }
    }, { immediate: true });

    onUnmounted(() => {
        document.body.classList.remove(lockClass);
        document.documentElement.classList.remove(lockClass);
    });
}