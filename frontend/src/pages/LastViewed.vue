<template>
  <Menu/>

  <div v-if="result?.totalCount" class="p-2">
    <h3 class="flex flex-column align-items-center gap-2">
      <span>Недавно просмотренные книги: {{result?.totalCount}} <i class="pi pi-book"/></span>
      <span>Из них прочитано страниц: {{result?.books.reduce((pages: number, book: any) => pages + book.readPages, 0)}} <i class="pi pi-file"/></span>
    </h3>
  </div>

  <div class="flex flex-wrap justify-content-center align-content-center">
    <template v-if="result">
      <div v-for="(book, index) in result.books" :key="index" class="border-round-2xl card flex flex-wrap justify-content-center m-2 p-2 p-card shadow-2">
        <div class="p-2 w-full">
          <MeterGroup class="meter-font" v-if="book.readPages" :value="[{label: verboseValue(book), value: percents(book), color: 'primary', icon: 'pi pi-file' }]"/>
        </div>
        <BookCard
            @select:publisher="filterBooksByPublisher"
            @select:tag="filterBooksByTag"
            :compactView="compactView"
            :book="book"
            class="m-0 p-0 clear-border"/>
      </div>
    </template>

    <!--Заглушка-->
    <template v-else-if="!result">
      <Skeleton v-for="i in [1,2,3,4]" :key="i" width="45rem" height="23.5rem" class="m-2 border-round-2xl shadow-2"></Skeleton>
    </template>

    <!--Нет прочитанных книг-->
    <template v-if="result?.books.length == 0">
      <div class="align-content-center flex flex-wrap w-full justify-content-center">
        <div class="flex justify-content-center w-full library-image">
        <div><h2 class="bg-gray-300 border-round-2xl p-3 m-3">Вы не начинали читать еще ни одной книги!</h2></div>
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
import TimeAgo from 'javascript-time-ago'
import ru from 'javascript-time-ago/locale/ru'

import Menu from "@/components/Menu.vue";
import Footer from "@/components/Footer.vue";
import BookCard from "@/components/BookCard.vue";
import SearchBookForm from "@/components/SearchBookForm.vue";

import BookViewStats from "@/components/BookViewStats.vue";
import {BookWithReadPages, BookWithReadPagesPaginatedResult} from "@/books";
import {FilterBook} from "@/filters";
import api from "@/services/api";


export default defineComponent({
  name: "ReadBooks",
  components: {BookViewStats, Footer, SearchBookForm, BookCard, Menu},
  data() {
    return {
      result: null as BookWithReadPagesPaginatedResult|null,
      filters: new FilterBook(),
      compactView: false,
    }
  },
  mounted() {
    TimeAgo.addDefaultLocale(ru)
    document.title = "Недавно просмотренные книги";
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
      api.get("/books/last-viewed" + urlParams)
          .then((value: AxiosResponse<BookWithReadPagesPaginatedResult>) => this.result = value.data)
    },

    filterBooksByPublisher(publisher: string) { document.location.href = "/?publisher=" + publisher;},
    filterBooksByTag(tag: string) { document.location.href = "/?tags=" + tag;},

    percents(book: BookWithReadPages) {
      return book.readPages/book.pages*100
    },
    verboseValue(book: BookWithReadPages) {
      return `Прочитано страниц: ${book.readPages}/${book.pages} | ` + this.verboseTimeAgo(book);
    },
    verboseTimeAgo(book: BookWithReadPages): string {
      const timeAgo = new TimeAgo('ru-RU')
      return book.lastTimeRead?timeAgo.format(new Date(book.lastTimeRead)):''
    }
  }
})
</script>

<style scoped>
.clear-border {
  border: none!important;
  box-shadow: none!important;
}

.card {
  -webkit-box-direction: normal!important;
  -ms-flex-direction: column!important;
  flex-direction: column!important;
  -webkit-box-orient: vertical!important;
}

.library-image {
  background-image: url("https://i.ytimg.com/vi/ODEql2yUK80/maxresdefault.jpg");
  background-size: auto;
  background-position: center top;
  background-repeat: no-repeat;
  height: 750px;
  font-family: "Monotype Corsiva", fantasy;
}

@media (width < 768px) {
  .card {
    width:100%!important;
    -webkit-box-direction: inherit!important;
    -ms-flex-direction: inherit!important;
    flex-direction: inherit!important;
    -webkit-box-orient: inherit!important;
  }

  .meter-font {
    font-size: 0.8rem;
  }
}

</style>