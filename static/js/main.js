if ('serviceWorker' in navigator) {
    window.addEventListener('load', async () => {
        try {
            const registration = await navigator.serviceWorker.register('/sw.js');
            console.log('ServiceWorker: Registrazione riuscita, scope:', registration.scope);
        } catch (error) {
            console.log('ServiceWorker: Registrazione fallita:', error);
        }
    });
}

import { createApp } from 'vue';
import Home from './views/Home.js';

const app = createApp(Home);

app.directive('click-outside', {
    beforeMount(el, binding) {
        el.clickOutsideEvent = function(event) {
            if (!(el === event.target || el.contains(event.target))) {
                binding.value(event, el);
            }
        };
        document.body.addEventListener('click', el.clickOutsideEvent);
    },
    unmounted(el) {
        document.body.removeEventListener('click', el.clickOutsideEvent);
    },
});

app.mount('#app');