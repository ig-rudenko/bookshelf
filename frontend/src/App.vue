<template>
  <router-view />
</template>
<script lang="ts">
import {defineComponent} from "vue";
import themeSwitch from "@/theming";
import { useRecaptchaProvider } from 'vue-recaptcha'

export default defineComponent({
  setup() {
    useRecaptchaProvider()
  },
  name: "App",
  mounted() {
    this.$primevue.changeTheme(themeSwitch.other, themeSwitch.current, "theme-link", () => {})
  }
});

</script>