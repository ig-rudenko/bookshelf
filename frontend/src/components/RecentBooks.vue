<script lang="ts">
import {defineComponent} from 'vue'
import {Book} from "@/books";
import api from "@/services/api.ts";
import {AxiosResponse} from "axios";

export default defineComponent({
  name: "RecentBooks",
  data() {
      return {
        recentBooks: [] as Book[]
      }
  },
  mounted() {
      this.getRecentBooks();
  },
  methods: {
    getRecentBooks() {
      api.get("/books/recent").then((res: AxiosResponse<Book[]>) => {this.recentBooks = res.data})
    }
  }
})
</script>

<template>
  <div class="flex justify-content-center">
    Последние добавленные
  </div>

  <div class="flex justify-content-center align-items-center">
    <div class="scroll-menu" style="width: 80rem;">
      <a :href="'/book/'+book.id" v-for="(book, index) in recentBooks" :key="index" class="item shadow-3">
        <img :alt="book.title" width="100%" :src="book.previewImage" v-tooltip.bottom="book.title" />
      </a>
    </div>
  </div>
</template>

<style scoped>
.scroll-menu {
  width: 100%;
  height: fit-content;

  /**used to scroll text*/
  white-space: nowrap;
  overflow-x: auto;
  overflow-y: hidden;

  /**keep scrolling when finger or cursor scrolling*/
  -webkit-overflow-scrolling: touch;
}
.item {
  margin: 0.5rem;
  width: 10rem;
  float: none;
  display: inline-block;
}
/*to hide the scrollbars*/
::-webkit-scrollbar {
  display: none;
}
</style>
