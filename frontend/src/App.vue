<script lang="ts">
import { defineComponent } from "vue";
import { useRecaptchaProvider } from "vue-recaptcha";

import Header from "@/components/Header.vue";
import Footer from "@/components/Footer.vue";

export default defineComponent({
    components: { Footer, Header },
    setup() {
        useRecaptchaProvider();
    },
    name: "App",
});
</script>

<template>
    <Header v-if="$route.name !== 'showBook'" />
    <main id="main-content" class="flex-1 min-w-0" tabindex="-1">
        <router-view />
    </main>
    <Footer />
</template>
