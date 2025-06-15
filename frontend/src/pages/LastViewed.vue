<template>
  <div v-if="result?.totalCount" class="p-2">
    <div class="p-3 sm:text-xl flex flex-col items-center gap-2 ">
      <div class="flex flex-wrap items-center justify-center gap-x-2 text-center">
        <span>Недавно просмотренные книги:</span>
        <span>{{ result?.totalCount }} <i class="pi pi-book"/></span>
      </div>
      <div class="flex flex-wrap items-center justify-center gap-x-2 text-center">
        <span>Из них прочитано страниц:</span>
        <span>
          {{ result?.books.reduce((pages: number, book: any) => pages + book.readPages, 0) }}
          <i class="pi pi-file"/>
        </span>
      </div>
    </div>
  </div>

  <div class="flex flex-wrap justify-center content-center gap-2 md:gap-4 w-full">
    <template v-if="result">
      <div v-for="(book, index) in result.books" :key="index"
           class="rounded-2xl flex-col flex flex-wrap border-1 border-gray-400 dark:border-gray-600 shadow-md hover:shadow-xl w-full md:w-auto">

        <div class="px-5 py-3 w-full border-b-1 border-gray-400 dark:border-gray-600">
          <MeterGroup class="text-xs sm:text-sm" v-if="book.readPages"
                      :value="[{label: verboseValue(book), value: percents(book), color: getReadPagesCountColor(percents(book)), icon: 'pi pi-file' }]"/>
        </div>
        <BookCard
            @select:publisher="filterBooksByPublisher"
            @select:tag="filterBooksByTag"
            @click:book="showBook"
            :image-classes="{'!rounded-t-none': true}"
            :compactView="compactView"
            :book="book"
            class="m-0 p-0 !border-0 !shadow-none"/>
      </div>
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
          <div><h2 class="border-round-2xl p-3 m-3">Нет недавно просмотренных книг</h2></div>
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
import TimeAgo from 'javascript-time-ago'
import ru from 'javascript-time-ago/locale/ru'

import BookCard from "@/components/BookCard.vue";
import SearchBookForm from "@/components/SearchBookForm.vue";

import BookViewStats from "@/components/BookViewStats.vue";
import {BookWithReadPages, BookWithReadPagesPaginatedResult} from "@/books";
import {FilterBook} from "@/filters";
import api from "@/services/api";
import {getReadPagesCountColor} from "@/formatter.ts";


export default defineComponent({
  name: "ReadBooks",
  components: {BookViewStats, SearchBookForm, BookCard},
  props: {
    userID: {type: Number, required: false, default: false}
  },
  data() {
    return {
      result: null as BookWithReadPagesPaginatedResult | null,
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
    getReadPagesCountColor,
    showBook(bookID: number) {
      document.location.href = `/book/${bookID}`;
    },

    getBooksList(page: number) {
      let url
      if (this.userID) {
        url = "/admin/users/" + this.userID + "/last-viewed"
      } else {
        url = "/bookmarks/last-viewed"
      }
      let urlParams = `?page=${page}`;
      api.get(url + urlParams)
          .then((value: AxiosResponse<BookWithReadPagesPaginatedResult>) => this.result = value.data)
    },

    filterBooksByPublisher(publisher: string) {
      document.location.href = "/?publisher=" + publisher;
    },
    filterBooksByTag(tag: string) {
      document.location.href = "/?tags=" + tag;
    },

    percents(book: BookWithReadPages) {
      return book.readPages / book.pages * 100
    },
    verboseValue(book: BookWithReadPages) {
      return `Прочитано страниц: ${book.readPages}/${book.pages} | ` + this.verboseTimeAgo(book);
    },
    verboseTimeAgo(book: BookWithReadPages): string {
      const timeAgo = new TimeAgo('ru-RU')
      return book.lastTimeRead ? timeAgo.format(new Date(book.lastTimeRead)) : ''
    }
  }
})
</script>
