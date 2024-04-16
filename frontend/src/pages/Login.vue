<script lang="ts">
import {defineComponent} from 'vue'

import Menu from "@/components/Menu.vue";
import LoginForm from "@/components/LoginForm.vue";
import Footer from "@/components/Footer.vue";

export default defineComponent({
  name: "Login",
  components: {Footer, Menu, LoginForm},
  mounted() {
      document.title = "Вход";
  },
});
</script>

<template>
  <Menu/>
  <div class="flex justify-content-center align-items-center pt-7">
    <LoginForm/>
  </div>
  <Footer/>
</template>

<style scoped>

</style>