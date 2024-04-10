<template>
  <Menu/>

  <div class="flex flex-wrap justify-content-center p-4">
    <SearchBookForm :filterData="filters" @filtered="(f) => {filters = f; getBooksList(1, f)}" />
  </div>

  <div v-if="results" class="flex flex-wrap justify-content-center align-content-center">
    <BookCard @select:tag="(t: any) => selectTag(t.name)" class="m-2" v-for="(book, index) in results.books" :key="index" :book="book"/>
  </div>
  <Paginator v-if="results"
      @page="(event: any) => getBooksList(event.page+1, filters)"
      @update:rows="(value: number) => results!.perPage = value"
      v-model="results.currentPage"
      :rows="results.perPage" :totalRecords="results.totalCount" :rowsPerPageOptions="[10, 25, 50]" />
</template>

<script lang="ts">
import Menu from "@/components/Menu.vue";
import {defineComponent} from 'vue'
import BookCard from "@/components/BookCard.vue";
import {Book} from "@/books.ts";
import api from "@/services/api.ts";
import {AxiosResponse} from "axios";
import SearchBookForm from "@/components/SearchBookForm.vue";
import {FilterBook, createFilterBook} from "@/filters.ts";


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
        filters: new FilterBook()
      }
  },
  mounted() {
    this.filters = createFilterBook(this.$route.query)
    this.getBooksList(1, this.filters);
  },
  methods: {
    getBooksList(page: number, filter: null|FilterBook=null) {
      let urlParams = `?page=${page}`;
      if (this.results) urlParams += `&per-page=${this.results.perPage}`;
      if (filter?.urlParams) urlParams += `&${filter.urlParams}`;

      history.pushState({ path: urlParams }, '', urlParams);

      api.get("/books" + urlParams)
          .then(
              (value: AxiosResponse<BookResult>) => this.results = value.data
          )
    },

    selectTag(tag: string) {
      if (!this.filters.tags.includes(tag)) {
        this.filters.tags.push(tag)
        this.getBooksList(1, this.filters);
      }
    }

  }
})
</script>

<style scoped>

</style>