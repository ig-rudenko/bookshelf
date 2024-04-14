<script lang="ts">
import {defineComponent} from 'vue'

import RegisterForm from "@/components/RegisterForm.vue";

export default defineComponent({
  name: "Register",
  components: {RegisterForm},
  mounted() {
    document.title = "Регистрация";
  }
});
</script>

<template>
<div class="flex justify-content-center align-items-center pt-7">
  <RegisterForm/>
</div>
</template>

<style scoped>

</style>