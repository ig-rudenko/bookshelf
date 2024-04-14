<script lang="ts">
import {defineComponent} from 'vue'

export default defineComponent({
  name: "ShowBook",
  computed: {
    bookId() {
      return this.$route.params.id
    }
  }
})
</script>

<template>
  <embed style="position:absolute; left: 0; top: 0;" height="100%" width="100%" :src="'/api/v1/books/'+bookId+'/download'">
</template>

<style scoped>

</style>