import { createApp } from 'vue';
import PrimeVue from 'primevue/config';
import "@/assets/main.css"
import "@/assets/styles.min.css"
import 'primeicons/primeicons.css'

import AutoComplete from "primevue/autocomplete/AutoComplete.vue";
import Avatar from "primevue/avatar";
import Badge from "primevue/badge";
import Button from "primevue/button";
import Card from "primevue/card";
import Chip from 'primevue/chip';
import Chips from 'primevue/chips';
import Dropdown from "primevue/dropdown";
import Dialog from "primevue/dialog";
import InlineMessage from "primevue/inlinemessage/InlineMessage.vue";
import FloatLabel from "primevue/floatlabel";
import FileUpload from "primevue/fileupload";
import InputNumber from "primevue/inputnumber";
import InputText from "primevue/inputtext";
import InputGroup from "primevue/inputgroup";
import InputGroupAddon from "primevue/inputgroupaddon";
import Menubar from "primevue/menubar";
import Password from "primevue/password";
import Textarea from "primevue/textarea";

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

app.component('AutoComplete', AutoComplete);
app.component('Avatar', Avatar);
app.component('Badge', Badge);
app.component('Button', Button);
app.component('Card', Card);
app.component('Chip', Chip);
app.component('Chips', Chips);
app.component('Dropdown', Dropdown);
app.component('Dialog', Dialog);
app.component('FloatLabel', FloatLabel);
app.component('FileUpload', FileUpload);
app.component('InlineMessage', InlineMessage);
app.component('InputNumber', InputNumber);
app.component('InputText', InputText);
app.component('InputGroupAddon', InputGroupAddon);
app.component('InputGroup', InputGroup);
app.component('Menubar', Menubar);
app.component('Password', Password);
app.component('Textarea', Textarea);

app.mount('#app');
