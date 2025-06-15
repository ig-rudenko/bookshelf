<template>
  <div class="flex flex-wrap justify-center p-3">
    <div class="sm:text-xl">Избранные книги: {{ result?.totalCount }}</div>
  </div>

  <div class="flex flex-wrap justify-center align-content-center">
    <template v-if="result">
      <BookCard
          v-for="(book, index) in result.books" :key="index"
          @select:publisher="filterBooksByPublisher"
          @select:tag="filterBooksByTag"
          @click:book="showBook"
          :compactView="compactView"
          :book="book"
          class="m-2"/>
    </template>

    <template v-else-if="!result">
      <!--Заглушка-->
      <Skeleton v-for="i in [1,2,3,4]" :key="i" width="45rem" height="23.5rem"
                class="m-2 border-round-2xl shadow-2"></Skeleton>
    </template>

    <!--Нет избранных книг-->
    <template v-if="result?.books.length == 0">
      <div class="align-content-center flex flex-wrap w-full justify-center">
        <div class="flex justify-center w-full">
          <div><h2 class="p-3 m-3">Нет избранных книг</h2></div>
        </div>
      </div>
    </template>

  </div>

  <Paginator v-if="result"
             :always-show="false"
             @page="(event: any) => getBooksList(event.page+1)"
             @update:rows="(value: number) => result!.perPage = value"
             v-model="result.currentPage"
             :rows="result.perPage" :totalRecords="result.totalCount" :rowsPerPageOptions="[10, 25, 50]"/>

</template>

<script lang="ts">
import {defineComponent} from 'vue';
import {AxiosResponse} from "axios";
import {mapState} from "vuex";

import BookCard from "@/components/BookCard.vue";

import SearchBookForm from "@/components/SearchBookForm.vue";
import {PaginatedBookResult} from "@/books";
import {FilterBook} from "@/filters";
import api from "@/services/api";


export default defineComponent({
  name: "Favorites",
  components: {SearchBookForm, BookCard},
  props: {
    userID: {type: Number, required: false, default: false}
  },
  data() {
    return {
      result: null as PaginatedBookResult | null,
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
    showBook(bookID: number) {
      document.location.href = `/book/${bookID}`;
    },
    getBooksList(page: number) {
      let url
      if (this.userID) {
        url = "/admin/users/" + this.userID + "/favorite"
      } else {
        url = "/bookmarks/favorite"
      }

      let urlParams = `?page=${page}`;

      api.get(url + urlParams)
          .then((value: AxiosResponse<PaginatedBookResult>) => this.result = value.data)
    },
    filterBooksByPublisher(publisher: string) {
      document.location.href = "/?publisher=" + publisher;
    },
    filterBooksByTag(tag: string) {
      document.location.href = "/?tags=" + tag;
    },

  }
})
</script>
