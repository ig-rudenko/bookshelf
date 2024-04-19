<template>
  <Menu/>

  <div class="flex flex-wrap justify-content-center p-2">
    <h2>Избранные книги: {{result?.totalCount}}</h2>
  </div>

  <div class="flex flex-wrap justify-content-center align-content-center">
    <template v-if="result">
      <BookCard
          v-for="(book, index) in result.books" :key="index"
          :compactView="compactView"
          :book="book"
          class="m-2"/>
    </template>

    <template v-else-if="!result">
      <!--Заглушка-->
      <Skeleton v-for="i in [1,2,3,4]" :key="i" width="45rem" height="23.5rem" class="m-2 border-round-2xl shadow-2"></Skeleton>
    </template>

    <!--Нет избранных книг-->
    <template v-if="result?.books.length == 0">
      <div class="align-content-center flex flex-wrap w-full justify-content-center">
        <div class="flex justify-content-center w-full">
        <div><h2 class="p-3 m-3">У вас нет избранных книг</h2></div>
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
  name: "Favorites",
  components: {Footer, SearchBookForm, BookCard, Menu},
  data() {
    return {
      result: null as PaginatedBookResult|null,
      filters: new FilterBook(),
      compactView: false,
    }
  },
  mounted() {
    document.title = "Избранные книги";
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
      api.get("/bookmarks/favorite" + urlParams)
          .then((value: AxiosResponse<PaginatedBookResult>) => this.result = value.data)
    },

  }
})
</script>

<style scoped>

</style>