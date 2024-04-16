<script lang="ts">
import {defineComponent} from 'vue'

import Menu from "@/components/Menu.vue";
import RegisterForm from "@/components/RegisterForm.vue";
import Footer from "@/components/Footer.vue";

export default defineComponent({
  name: "Register",
  components: {Footer, Menu, RegisterForm},
  mounted() {
    document.title = "Регистрация";
  }
});
</script>

<template>
  <Menu/>
  <div class="flex justify-content-center align-items-center pt-7">
    <RegisterForm/>
  </div>
  <Footer/>
</template>

<style scoped>

</style>