import {
    Accordion,
    AccordionContent,
    AccordionHeader,
    AccordionPanel,
    AutoComplete,
    Avatar,
    Badge,
    Button,
    Card,
    Carousel,
    Chip,
    ConfirmationService,
    DeferredContent,
    Dialog,
    FileUpload,
    FloatLabel,
    IconField,
    InputChips,
    InputGroup,
    InputGroupAddon,
    InputIcon,
    InputNumber,
    InputText,
    MegaMenu,
    Menu,
    Message,
    MeterGroup,
    Paginator,
    Password,
    Popover,
    ScrollPanel,
    Select,
    Skeleton,
    Textarea,
    Tooltip
} from "primevue";
import 'primeicons/primeicons.css'
import {VueRecaptchaPlugin} from 'vue-recaptcha';
import {createHead} from "@unhead/vue";

import {app} from '@/appInstance';
import store from "@/store";
import ToastService from 'primevue/toastservice';
import setupInterceptors from '@/services/setupInterceptors';
import router from "@/router";

const head = createHead()
setupInterceptors(store);
app.use(head)
app.use(VueRecaptchaPlugin, {v2SiteKey: '6LcpBc0pAAAAAHu7T0s0SpoqfEgW2iQk-XCX5hwp'})

app.use(ToastService);
app.use(ConfirmationService);
app.directive('tooltip', Tooltip);
app.use(store);
app.use(router);

app.component('AutoComplete', AutoComplete);
app.component('Accordion', Accordion);
app.component('AccordionPanel', AccordionPanel);
app.component('AccordionContent', AccordionContent);
app.component('AccordionHeader', AccordionHeader);
app.component('Avatar', Avatar);
app.component('Badge', Badge);
app.component('Button', Button);
app.component('Card', Card);
app.component('Carousel', Carousel);
app.component('Chip', Chip);
app.component('Chips', InputChips);
app.component('DeferredContent', DeferredContent);
app.component('Select', Select);
app.component('Dialog', Dialog);
app.component('FloatLabel', FloatLabel);
app.component('FileUpload', FileUpload);
app.component('IconField', IconField);
app.component('InputIcon', InputIcon);
app.component('Message', Message);
app.component('InputNumber', InputNumber);
app.component('InputText', InputText);
app.component('InputGroupAddon', InputGroupAddon);
app.component('InputGroup', InputGroup);
app.component('Menu', Menu);
app.component('MegaMenu', MegaMenu);
app.component('MeterGroup', MeterGroup);
app.component('Popover', Popover);
app.component('Paginator', Paginator);
app.component('Password', Password);
app.component('Skeleton', Skeleton);
app.component('Textarea', Textarea);
app.component('ScrollPanel', ScrollPanel);

app.mount('#app');
