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
  <div class="mx-auto w-full sm:w-[650px] pt-7">
    <RegisterForm/>
  </div>
</template>
