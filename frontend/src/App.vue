<template>
  <router-view/>
</template>
<script lang="ts">
import {defineComponent} from "vue";
import themeSwitch from "@/theming";

export default defineComponent({
  name: "App",
  mounted() {
    this.$primevue.changeTheme(themeSwitch.other, themeSwitch.current, "theme-link", () => {})
  }
});

</script>