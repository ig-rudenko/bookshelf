import { createApp } from 'vue';
import PrimeVue from 'primevue/config';
import "@/assets/styles.min.css"
import "@/assets/main.css"
import 'primeicons/primeicons.css'
import 'primevue/resources/themes/aura-light-green/theme.css';

import Button from "primevue/button";

import App from '@/App.vue';
import store from "@/store";
import ToastService from 'primevue/toastservice';
import setupInterceptors from '@/services/setupInterceptors';
import createRouter from "@/router";

setupInterceptors(store);
const app = createApp(App);
app.use(PrimeVue, { ripple: true });
app.use(ToastService);
app.use(store);
app.use(createRouter());

app.component('Button', Button);

app.mount('#app');
