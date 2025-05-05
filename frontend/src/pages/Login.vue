<script lang="ts">
import {defineComponent} from 'vue'

import LoginForm from "@/components/LoginForm.vue";

export default defineComponent({
  name: "Login",
  components: {LoginForm},
  mounted() {
    document.title = "Вход";
  },
});
</script>

<template>
  <div class="mx-auto w-full sm:w-[650px] pt-7">
    <LoginForm/>
  </div>
</template>

