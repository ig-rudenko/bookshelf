import { createApp } from 'vue';
import PrimeVue from 'primevue/config';
import "@/assets/main.css"
import "@/assets/styles.min.css"
import 'primeicons/primeicons.css'

import AutoComplete from "primevue/autocomplete/AutoComplete.vue";
import Accordion from "primevue/accordion";
import AccordionTab from "primevue/accordiontab";
import Avatar from "primevue/avatar";
import Badge from "primevue/badge";
import Button from "primevue/button";
import Card from "primevue/card";
import Chip from 'primevue/chip';
import Chips from 'primevue/chips';
import DeferredContent from 'primevue/deferredcontent';
import Dropdown from "primevue/dropdown";
import Dialog from "primevue/dialog";
import InlineMessage from "primevue/inlinemessage/InlineMessage.vue";
import FloatLabel from "primevue/floatlabel";
import FileUpload from "primevue/fileupload";
import IconField from "primevue/iconfield";
import InputNumber from "primevue/inputnumber";
import InputIcon from "primevue/inputicon";
import InputText from "primevue/inputtext";
import InputGroup from "primevue/inputgroup";
import InputGroupAddon from "primevue/inputgroupaddon";
import Menu from "primevue/menu";
import MegaMenu from "primevue/megamenu";
import MeterGroup from "primevue/metergroup";
import OverlayPanel from "primevue/overlaypanel";
import Paginator from "primevue/paginator";
import Password from "primevue/password";
import Skeleton from 'primevue/skeleton';
import Textarea from "primevue/textarea";
import Tooltip from 'primevue/tooltip';
import ScrollPanel from "primevue/scrollpanel";
// import {Router} from "vue-router";
import { VueRecaptchaPlugin } from 'vue-recaptcha';
import {createHead} from "@unhead/vue";

import App from '@/App.vue';
import store from "@/store";
import ToastService from 'primevue/toastservice';
import setupInterceptors from '@/services/setupInterceptors';
import router from "@/router";

const head = createHead()
setupInterceptors(store);
const app = createApp(App);
app.use(head)
app.use(VueRecaptchaPlugin, { v2SiteKey: '6LcpBc0pAAAAAHu7T0s0SpoqfEgW2iQk-XCX5hwp' })
app.use(PrimeVue, { ripple: true });
app.use(ToastService);
app.directive('tooltip', Tooltip);
app.use(store);
app.use(router);
// app.config.globalProperties.$router = router as Router;

app.component('AutoComplete', AutoComplete);
app.component('Accordion', Accordion);
app.component('AccordionTab', AccordionTab);
app.component('Avatar', Avatar);
app.component('Badge', Badge);
app.component('Button', Button);
app.component('Card', Card);
app.component('Chip', Chip);
app.component('Chips', Chips);
app.component('DeferredContent', DeferredContent);
app.component('Dropdown', Dropdown);
app.component('Dialog', Dialog);
app.component('FloatLabel', FloatLabel);
app.component('FileUpload', FileUpload);
app.component('IconField', IconField);
app.component('InputIcon', InputIcon);
app.component('InlineMessage', InlineMessage);
app.component('InputNumber', InputNumber);
app.component('InputText', InputText);
app.component('InputGroupAddon', InputGroupAddon);
app.component('InputGroup', InputGroup);
app.component('Menu', Menu);
app.component('MegaMenu', MegaMenu);
app.component('MeterGroup', MeterGroup);
app.component('OverlayPanel', OverlayPanel );
app.component('Paginator', Paginator);
app.component('Password', Password);
app.component('Skeleton', Skeleton);
app.component('Textarea', Textarea);
app.component('ScrollPanel', ScrollPanel);

app.mount('#app');
