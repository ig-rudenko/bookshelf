<template>
  <Menu/>

  <div v-if="result?.totalCount" class="p-2">
    <h3 class="flex flex-column align-items-center gap-2">
      <span>Прочитанных книг: {{result?.totalCount}} <i class="pi pi-book"/></span>
      <span>Всего страниц: {{result?.books.reduce((pages: number, book: any) => pages + book.pages, 0)}} <i class="pi pi-file"/></span>
    </h3>
  </div>

  <div class="flex flex-wrap justify-content-center align-content-center">
    <template v-if="result">
      <BookCard
          v-for="(book, index) in result.books" :key="index"
          @select:publisher="filterBooksByPublisher"
          @select:tag="filterBooksByTag"
          :compactView="compactView"
          :book="book"
          class="m-2"/>
    </template>

    <!--Заглушка-->
    <template v-else-if="!result">
      <Skeleton v-for="i in [1,2,3,4]" :key="i" width="45rem" height="23.5rem" class="m-2 border-round-2xl shadow-2"></Skeleton>
    </template>

    <!--Нет прочитанных книг-->
    <template v-if="result?.books.length == 0">
      <div class="align-content-center flex flex-wrap w-full justify-content-center">
        <div class="flex justify-content-center w-full library-image">
        <div><h2 class="bg-gray-300 border-round-2xl p-3 m-3">Вы не прочли еще ни одной книги!</h2></div>
        </div>
      </div>
    </template>

  </div>

  <Paginator v-if="result"
      :always-show="false"
      @page="(event: any) => getBooksList(event.page+1)"
      @update:rows="(value: number) => result!.perPage = value"
      v-model="result.currentPage"
      :rows="result.perPage" :totalRecords="result.totalCount" :rowsPerPageOptions="[10, 25, 50]" />

  <Footer/>

</template>

<script lang="ts">
import {defineComponent} from 'vue';
import {AxiosResponse} from "axios";
import {mapState} from "vuex";

import Menu from "@/components/Menu.vue";
import Footer from "@/components/Footer.vue";
import BookCard from "@/components/BookCard.vue";
import SearchBookForm from "@/components/SearchBookForm.vue";

import {PaginatedBookResult} from "@/books";
import {FilterBook} from "@/filters";
import api from "@/services/api";


export default defineComponent({
  name: "ReadBooks",
  components: {Footer, SearchBookForm, BookCard, Menu},
  data() {
    return {
      result: null as PaginatedBookResult|null,
      filters: new FilterBook(),
      compactView: false,
    }
  },
  mounted() {
    document.title = "Прочитанные книги";
    if (!this.loggedIn) this.$router.push("/login");
    this.getBooksList(1);
  },
  computed: {
    ...mapState({
      loggedIn: (state: any) => state.auth.status.loggedIn,
    }),
  },
  methods: {
    getBooksList(page: number) {
      let urlParams = `?page=${page}`;
      api.get("/bookmarks/read" + urlParams)
          .then((value: AxiosResponse<PaginatedBookResult>) => this.result = value.data)
    },

    filterBooksByPublisher(publisher: string) { document.location.href = "/?publisher=" + publisher;},
    filterBooksByTag(tag: string) { document.location.href = "/?tags=" + tag;},

  }
})
</script>

<style scoped>
.library-image {
  background-image: url("https://i.ytimg.com/vi/ODEql2yUK80/maxresdefault.jpg");
  background-size: auto;
  background-position: center top;
  background-repeat: no-repeat;
  height: 750px;
  font-family: "Monotype Corsiva", fantasy;
}
</style>