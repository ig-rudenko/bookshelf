<template>
  <Menu/>

  <div class="flex flex-wrap justify-content-center p-4">
    <SearchBookForm/>
  </div>

  <div v-if="results" class="flex flex-wrap justify-content-center align-content-center">
    <BookCard class="m-2" v-for="(book, index) in results.books" :key="index" :book="book"/>
  </div>
  <Paginator v-if="results"
      @page="(event: any) => getBooksList(event.page+1)"
      @update:rows="(value: number) => results!.perPage = value"
      v-model="results.currentPage"
      :rows="results.perPage" :totalRecords="results.totalCount" :rowsPerPageOptions="[2, 25, 50]" />
</template>

<script lang="ts">
import Menu from "@/components/Menu.vue";
import {defineComponent} from 'vue'
import BookCard from "@/components/BookCard.vue";
import {Book} from "@/books.ts";
import api from "@/services/api.ts";
import {AxiosResponse} from "axios";
import SearchBookForm from "@/components/SearchBookForm.vue";


class BookResult {
  constructor(
      public books: Book[],
      public totalCount: number,
      public currentPage: number,
      public maxPages: number,
      public perPage: number
  ) {}
}


export default defineComponent({
  name: "Home",
  components: {SearchBookForm, BookCard, Menu},
  data() {
      return {
        results: null as BookResult|null,
      }
  },
  mounted() {
    this.getBooksList(1);
  },
  methods: {
    getBooksList(page: number) {
      let url = `/books?page=${page}`
      if (this.results) {
        url += `&per-page=${this.results.perPage}`
      }
      api.get(url)
          .then(
              (value: AxiosResponse<BookResult>) => this.results = value.data
          )
    },
  }
})
</script>

<style scoped>

</style>