<script lang="ts">
import {defineComponent} from 'vue'

import LoginForm from "@/components/LoginForm.vue";

export default defineComponent({
  name: "Login",
  components: {LoginForm}
});
</script>

<template>
<div class="flex justify-content-center align-items-center pt-7">
  <LoginForm/>
</div>
</template>

<style scoped>

</style>