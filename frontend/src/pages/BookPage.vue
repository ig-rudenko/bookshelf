<template>
  <Menu/>

</template>

<script lang="ts">
import {defineComponent} from 'vue'
import Menu from "@/components/Menu.vue";
import {Book} from "@/books.ts";
import api from "@/services/api.ts";
import {AxiosResponse} from "axios";

export default defineComponent({
  name: "BookPage",
  components: {Menu,},
  data() {
      return {
        book: null as Book|null,
      }
  },
  mounted() {
      this.getBook();
  },
  methods: {
    getBook() {
      if (!this.book) return;
      api.get(`/books/${this.book.id}`)
          .then(
              (value: AxiosResponse<Book>) => {
                this.book = value.data;
              }
          )
    }
  }
})
</script>

<style scoped>

</style>