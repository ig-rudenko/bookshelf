import { createApp } from 'vue';
import PrimeVue from 'primevue/config';
import "@/assets/main.css"
import "@/assets/styles.min.css"
import 'primeicons/primeicons.css'
// import 'primevue/resources/themes/soho-light/theme.css';

import Avatar from "primevue/avatar";
import Badge from "primevue/badge";
import Button from "primevue/button";
import Dialog from "primevue/dialog";
import InlineMessage from "primevue/inlinemessage/InlineMessage.vue";
import FloatLabel from "primevue/floatlabel";
import InputText from "primevue/inputtext";
import InputGroup from "primevue/inputgroup";
import InputGroupAddon from "primevue/inputgroupaddon";
import Menubar from "primevue/menubar";
import Password from "primevue/password";

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

app.component('Avatar', Avatar);
app.component('Badge', Badge);
app.component('Button', Button);
app.component('Dialog', Dialog);
app.component('FloatLabel', FloatLabel);
app.component('InlineMessage', InlineMessage);
app.component('InputText', InputText);
app.component('InputGroupAddon', InputGroupAddon);
app.component('InputGroup', InputGroup);
app.component('Menubar', Menubar);
app.component('Password', Password);

app.mount('#app');
