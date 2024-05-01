<script lang="ts">
import {defineComponent} from 'vue'

import Menu from "@/components/Menu.vue";
import EmailSend from "@/components/EmailSend.vue";
import Footer from "@/components/Footer.vue";

export default defineComponent({
  name: "Login",
  components: {Footer, Menu, EmailSend},
  mounted() {
      document.title = "Забыли пароль";
  },
});
</script>

<template>
  <Menu/>
  <div class="flex justify-content-center align-items-center pt-7">
    <EmailSend/>
  </div>
  <Footer/>
</template>

<style scoped>

</style>