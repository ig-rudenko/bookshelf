import { createApp } from 'vue';
import App from './App.vue';
import 'primevue/resources/themes/aura-light-green/theme.css';
import PrimeVue from 'primevue/config';

import Button from "primevue/button";

const app = createApp(App);
app.use(PrimeVue,  { ripple: true });
app.component('Button', Button);
app.mount('#app');
