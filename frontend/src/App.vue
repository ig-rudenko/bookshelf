<script lang="ts">
import {defineComponent} from "vue";
import {useRecaptchaProvider} from 'vue-recaptcha';

import Header from "@/components/Header.vue";
import Footer from "@/components/Footer.vue";

export default defineComponent({
  components: {Footer, Header},
  setup() {
    useRecaptchaProvider()
  },
  name: "App",
});
</script>

<template>
  <Header/>
  <router-view/>
  <Footer/>
</template>
