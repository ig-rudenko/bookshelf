<template>
  <Menu/>

  <div class="mt-4">
    <RecentBooks/>
  </div>

  <div class="flex flex-wrap justify-content-center p-2">
    <SearchBookForm
        @compactView="v => compactView = v"
        :filterData="filters" @filtered="(f) => {filters = f; getBooksList(1, f)}" />
  </div>

  <div class="flex flex-wrap justify-content-center align-content-center">
    <template v-if="results">
      <BookCard
          @select:tag="selectTag"
          @select:publisher="selectPublisher"
          v-for="(book, index) in results.books" :key="index"
          :compactView="compactView"
          :book="book"
          class="m-2"/>
    </template>

    <template v-else>
      <!--Заглушка-->
      <Skeleton v-for="i in [1,2,3,4]" :key="i" width="45rem" height="23.5rem" class="m-2 border-round-2xl shadow-2"></Skeleton>
    </template>
  </div>

  <Paginator v-if="results"
             @page="(event: any) => getBooksList(event.page+1, filters)"
             @update:rows="(value: number) => results!.perPage = value"
             :pages="3"
             v-model="results.currentPage"
             :rows="results.perPage" :totalRecords="results.totalCount" :rowsPerPageOptions="[10, 25, 50]" />

  <Footer/>

</template>

<script lang="ts">
import {defineComponent} from 'vue';
import {AxiosResponse} from "axios";

import Menu from "@/components/Menu.vue";
import Footer from "@/components/Footer.vue";
import BookCard from "@/components/BookCard.vue";
import SearchBookForm from "@/components/SearchBookForm.vue";

import {PaginatedBookResult} from "@/books";
import api from "@/services/api";
import {createFilterBook, FilterBook} from "@/filters";
import RecentBooks from "@/components/RecentBooks.vue";


export default defineComponent({
  name: "Home",
  components: {RecentBooks, Footer, SearchBookForm, BookCard, Menu},
  data() {
      return {
        results: null as PaginatedBookResult|null,
        filters: new FilterBook(),
        compactView: false,
        windowWidth: window.innerWidth,
      }
  },
  mounted() {
    this.filters = createFilterBook(this.$route.query)
    this.getBooksList(1, this.filters);
    window.addEventListener('resize', () => this.windowWidth = window.innerWidth);
  },
  computed: {
    isMobile() {
      return this.windowWidth <= 768;
    },
  },
  methods: {
    getBooksList(page: number, filter: null|FilterBook=null) {
      let urlParams = `?page=${page}`;
      if (this.results) urlParams += `&per-page=${this.results.perPage}`;
      if (filter?.urlParams) urlParams += `&${filter.urlParams}`;

      history.pushState({ path: urlParams }, '', urlParams);

      api.get("/books" + urlParams)
          .then(
              (value: AxiosResponse<PaginatedBookResult>) => this.results = this.replaceThumb(value.data)
          )
    },

    replaceThumb(data: PaginatedBookResult): PaginatedBookResult {
      if (this.isMobile) {
        for (const book of data.books) {
          book.previewImage = book.previewImage.replace("medium.png", "small.png")
        }
      }
      return data
    },

    selectTag(tag: string) {
      if (!this.filters.tags.includes(tag)) {
        this.filters.tags.push(tag)
        this.getBooksList(1, this.filters);
      }
    },

    selectPublisher(publisherName: string) {
      this.filters.publisher = publisherName;
      this.getBooksList(1, this.filters);
    }

  }
})
</script>

<style scoped>

</style>