<script lang="ts">
import {defineComponent} from 'vue'

import EmailSend from "@/components/EmailSend.vue";

export default defineComponent({
  name: "Login",
  components: {EmailSend},
  mounted() {
    document.title = "Забыли пароль";
  },
});
</script>

<template>
  <div class="mx-auto w-full sm:w-[650px] pt-7">
    <EmailSend/>
  </div>
</template>
