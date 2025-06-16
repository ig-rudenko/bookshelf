<template>
  <div id="search-block" class="flex flex-wrap justify-center p-2">
    <SearchBookForm
        :initialCompactView="initialCompactView"
        @compactView="(v: boolean) => compactView = v"
        :filterData="filters" @filtered="(f: any) => {filters = f; getBooksList(1, f)}"/>
  </div>

  <div class="flex flex-wrap justify-center content-center gap-2 md:gap-5 p-2"
       :class="{'!gap-x-1 md:!gap-x-3 items-baseline gap-y-4': compactView}">
    <template v-if="results && !loadingBooks">
      <BookCard
          @click:book="book => $emit('click:book', book)"
          @select:tag="selectTag"
          @select:publisher="selectPublisher"
          v-for="(book, index) in results.books" :key="index"
          :compactView="compactView"
          :book="book"/>
    </template>

    <template v-else-if="loadingBooks">
      <!--Заглушка-->
      <Skeleton v-for="i in [1,2,3,4]" :key="i" width="45rem" height="23.5rem"
                class="m-2 rounded-2xl shadow-xl"></Skeleton>
    </template>

  </div>

  <Paginator v-if="results?.totalCount" class="text-xs md:text-base"
             @page="(event: any) => getBooksList(event.page+1, filters)"
             @update:rows="(value: number) => results!.perPage = value"
             :pages="3"
             :always-show="false"
             v-model="results.currentPage"
             :rows="results.perPage" :totalRecords="results.totalCount"
             :rowsPerPageOptions="[10, 25, 50]"/>

  <div v-else>
    <div class="flex justify-center content-center text-center text-2xl font-bold py-4">Нет результатов по вашему
      запросу
    </div>
  </div>

</template>

<script lang="ts">
import {defineComponent} from 'vue'
import {PaginatedBookResult} from "@/books.ts";
import {createFilterBook, FilterBook} from "@/filters.ts";
import bookService from "@/services/books.ts";
import SearchBookForm from "@/components/SearchBookForm.vue";
import BookCard from "@/components/BookCard.vue";

export default defineComponent({
  name: "FullSearchBooks",
  components: {BookCard, SearchBookForm},
  props: {
    initialPerPage: {required: false, type: Number, default: 25},
    initialCompactView: {required: false, type: Boolean, default: false},
    authScrollToSearchBlock: {required: false, type: Boolean, default: true},
  },
  emits: ['click:book'],

  data() {
    return {
      results: null as PaginatedBookResult | null,
      lastUrlParams: "",
      filters: new FilterBook(),
      compactView: this.initialCompactView,
      windowWidth: window.innerWidth,
      loadingBooks: false,
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
    getBooksList(page: number, filter: null | FilterBook = null) {
      this.loadingBooks = true
      if (this.authScrollToSearchBlock) location.hash = "#search-block";

      bookService.getBooksList(page, filter, this.results?.perPage || this.initialPerPage).then(
          (value: PaginatedBookResult | null) => {
            if (value) this.results = this.replaceThumb(value);
            this.loadingBooks = false;
          }
      ).catch(() => {
        this.loadingBooks = false
      })
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
