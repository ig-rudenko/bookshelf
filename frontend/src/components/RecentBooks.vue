<script lang="ts">
import {defineComponent} from 'vue'
import {Book} from "@/books";
import api from "@/services/api";
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
      api.get("/books/recent").then((res: AxiosResponse<Book[]>) => {
        this.recentBooks = res.data
      })
    }
  }
})
</script>

<template>
  <div class="pt-5">
    <div class="flex justify-center">
      Последние добавленные
    </div>

    <div class="flex justify-center items-center">
      <div class="scroll-menu" style="width: 80rem;">
        <a :href="'/book/'+book.id" v-for="(book, index) in recentBooks" :key="index" class="m-2 inline-block shadow-3">
          <img :alt="book.title" class="item flex" :src="book.previewImage.replace('.png', '_thumb_medium.png')"
               v-tooltip.bottom="book.title"/>
        </a>
      </div>
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
  height: 100%;
  max-height: 220px;
  float: none;
  display: inline-block;
}

.scroll-menu::-webkit-scrollbar {
  display: inline;
  height: 5px;
}

.scroll-menu::-webkit-scrollbar-track-piece {
  background-color: var(--p-primary-100);
  border-radius: 20px;
}

.scroll-menu::-webkit-scrollbar-thumb {
  background-color: var(--p-primary-300);
  border-radius: 20px;
  height: 4px;
}

.scroll-menu::-webkit-scrollbar-thumb:hover {
  background-color: var(--p-primary-500);
}
</style>
