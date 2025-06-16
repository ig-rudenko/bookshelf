<template>
  <div v-if="result?.totalCount" class="p-2">
    <div class="p-3 sm:text-xl flex flex-col items-center gap-2">
      <div class="flex flex-wrap items-center justify-center gap-x-2 text-center">
        <div>Прочитанных книг:</div>
        <div>{{ result?.totalCount }} <i class="pi pi-book"/></div>
      </div>
      <div class="flex flex-wrap items-center justify-center gap-x-2 text-center">
        <span>Всего страниц:</span>
        <span>
          {{ result?.books.reduce((pages: number, book: any) => pages + book.pages, 0) }} <i class="pi pi-file"/>
        </span>
      </div>
    </div>
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

    <!--Заглушка-->
    <template v-else-if="!result">
      <Skeleton v-for="i in [1,2,3,4]" :key="i" width="45rem" height="23.5rem"
                class="m-2 border-round-2xl shadow-2"></Skeleton>
    </template>

    <!--Нет прочитанных книг-->
    <template v-if="result?.books.length == 0">
      <div class="align-content-center flex flex-wrap w-full justify-center">
        <div class="flex justify-center w-full library-image">
          <div><h2 class="border-round-2xl p-3 m-3">Не было прочитано еще ни одной книги!</h2></div>
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
import {mapState} from "vuex";

import BookCard from "@/components/BookCard.vue";
import SearchBookForm from "@/components/SearchBookForm.vue";

import {Book, PaginatedBookResult} from "@/books";
import {FilterBook} from "@/filters";
import api from "@/services/api";


export default defineComponent({
  name: "ReadBooks",
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
    showBook(book: Book) {
      document.location.href = `/book/${book.id}`;
    },
    getBooksList(page: number) {
      let url
      if (this.userID) {
        url = "/admin/users/" + this.userID + "/read"
      } else {
        url = "/bookmarks/read"
      }
      let urlParams = `?page=${page}`;
      api.get<PaginatedBookResult>(url + urlParams)
          .then(value => this.result = value.data)
    },

    filterBooksByPublisher(publisher: string) {
      document.location.href = "/?publisher=" + encodeURIComponent(publisher);
    },
    filterBooksByTag(tag: string) {
      document.location.href = "/?tags=" + encodeURIComponent(tag);
    },

  }
})
</script>
