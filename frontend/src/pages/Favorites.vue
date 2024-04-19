<template>
  <Menu/>

  <div class="flex flex-wrap justify-content-center p-2">
    <h2>Избранные книги: {{books?.length}}</h2>
  </div>

  <div class="flex flex-wrap justify-content-center align-content-center">
    <template v-if="books !== null">
      <BookCard
          v-for="(book, index) in books" :key="index"
          :compactView="compactView"
          :book="book"
          class="m-2"/>
    </template>

    <template v-else>
      <!--Заглушка-->
      <Skeleton v-for="i in [1,2,3,4]" :key="i" width="45rem" height="23.5rem" class="m-2 border-round-2xl shadow-2"></Skeleton>
    </template>
  </div>

  <Footer/>

</template>

<script lang="ts">
import {defineComponent} from 'vue';
import {AxiosResponse} from "axios";

import Menu from "@/components/Menu.vue";
import Footer from "@/components/Footer.vue";
import BookCard from "@/components/BookCard.vue";
import SearchBookForm from "@/components/SearchBookForm.vue";

import {Book} from "@/books";
import api from "@/services/api";
import {FilterBook} from "@/filters";
import {mapState} from "vuex";


export default defineComponent({
  name: "Favorites",
  components: {Footer, SearchBookForm, BookCard, Menu},
  data() {
    return {
      books: null as Book[]|null,
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
          .then((value: AxiosResponse<Book[]>) => this.books = value.data)
    },

  }
})
</script>

<style scoped>

</style>