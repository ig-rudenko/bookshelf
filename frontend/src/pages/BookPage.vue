<template>
  <div v-if="book" class="flex flex-wrap justify-center mb-4">
    <div class="flex flex-col">
      <div class="xl:hidden p-3 py-5 text-2xl font-bold text-center">{{ book.title }}</div>
      <a :href="'/book/'+book.id+'/show'" target="_blank" class="flex flex-col py-5 sticky top-[1rem]">
        <img class="rounded-xl" alt="book" :src="book.previewImage"/>
      </a>
    </div>

    <div class="flex flex-col m-3 w-full max-w-[40rem]">
      <div class="hidden md:block p-2 text-2xl font-bold text-center py-10">{{ book.title }}</div>

      <div v-if="loggedIn && user" class="mb-3 flex flex-wrap items-center not-md:justify-center gap-2">
        <Bookmarks type="favorite" :bookId="book.id" :mark="book.favorite"
                   @updated="(v: boolean) => book!.favorite = v"/>
        <Bookmarks type="read" :bookId="book.id" :mark="book.read" @updated="(v: boolean) => book!.read = v"/>

        <template v-if="user.id == book.userId">
          <Button @click="showEditBook" v-tooltip.bottom="'Редактировать'" icon="pi pi-pencil" raised rounded outlined
                  severity="warn"/>
          <Button @click="displayDeleteBookDialog = true" v-tooltip.bottom="'Удалить'" icon="pi pi-trash" raised rounded
                  outlined severity="danger"/>
          <Button v-if="book.private && user.id == book.userId" size="small" icon="pi pi-lock" rounded outlined raised
                  v-tooltip.bottom="'Никто её не видит'" label="Это ваша личная книга."/>
        </template>
      </div>

      <div v-if="book.bookshelves" class="m-2">
        <div class="text-right">
          <i class="pi pi-book"/> Книжные полки:
        </div>
        <div class="m-2 flex flex-row flex-wrap justify-end items-center gap-2 text-xs">
          <a :href="'/bookshelves?search='+encodeURIComponent(bookshelf.name)" v-for="bookshelf in book.bookshelves"
             :key="bookshelf.id">
            <Button v-tooltip.bottom="'Перейдите на страницу полки'" size="small"
                    severity="contrast" class="hover:shadow-md"
                    :icon="bookshelf.private?'pi pi-lock':''"
                    outlined :label="bookshelf.name"/>
          </a>
        </div>
      </div>

      <BookViewStats v-if="loggedIn" :book="book"/>

      <Divider/>

      <div class="m-2">
        <span>Издательство <i class="pi pi-building mr-2"/></span>
        <a :href="'/?publisher='+book.publisher.name" class="text-primary no-underline"
           v-tooltip.bottom="'Фильтр по издателю'">{{ book.publisher.name }}</a>
        <span class="ml-2" v-tooltip="'Год публикации оригинала'">{{ book.year }} г.</span>
      </div>
      <div class="m-2 flex flex-row items-center gap-2">
        <span>Язык книги: {{ book.language }}</span>
        <img :alt="book.language" :src="`https://flagcdn.com/${getLanguagePairByLabel(book.language).code}.svg`"
             class="ml-1 border-1 border-gray-500" style="width: 18px"/>
      </div>
      <div class="m-2">
        <i class="pi pi-users"/> {{ book.authors }}
      </div>
      <div class="m-2 space-x-2">
        <i class="pi pi-book"/>{{ book.pages }} стр.
        <span :class="{'text-red-400': book.size > 50*1024*1024, 'text-orange-400': book.size > 30*1024*1024}">
          <i class="pi pi-file"/> {{ formatBytes(book.size) }}
        </span>
        <span @click="downloadBook" class="cursor-pointer hover:text-purple-400"><i class="pi pi-download mx-2"/>Загрузить</span>
      </div>
      <div class="m-2 chips">
        <a :href="'/?tags='+encodeURIComponent(tag.name)" v-for="(tag, index) in book.tags">
          <Badge v-tooltip.bottom="'Найти похожие'" size="large" class="m-1" icon="pi pi-tag" :key="index">
            {{ tag.name }}
          </Badge>
        </a>
      </div>

      <Divider/>
      <div class="px-3 w-full text-justify" v-html="textToHtml(wrapLinks(book.description))"></div>
    </div>
  </div>

  <Divider/>

  <div v-if="book?.id && canCreateComment" class="flex justify-center">
    <CreateComment @created="getComments(1)" :book-id="book.id"/>
  </div>

  <div class="flex flex-wrap flex-col items-center pt-4 p-2" v-if="results">
    <Comment @comment:delete="getComments(1)" @comment:update="getComments(1)"
             v-for="(comment, index) in results.comments" :key="index" :comment="comment"/>
    <Paginator class="w-full" v-if="results"
               :always-show="false"
               @page="(event: any) => getComments(event.page+1)"
               @update:rows="(value: number) => results!.perPage = value"
               v-model="results.currentPage"
               :rows="results.perPage" :totalRecords="results.totalCount" :rowsPerPageOptions="[10, 25, 50]"/>
  </div>

  <Dialog v-model:visible="displayDeleteBookDialog" :show-header="false" modal>
    <div class="text-xl flex items-center gap-4 py-5">
      <i class="pi pi-exclamation-circle text-red-500 !text-3xl"/>
      Вы уверены, что хотите удалить эту книгу?
    </div>
    <div class="flex justify-center sm:justify-end gap-2">
      <Button type="button" severity="success" icon="pi pi-times" label="Не удалять" autofocus
              @click="displayDeleteBookDialog = false"></Button>
      <Button type="button" icon="pi pi-trash" severity="danger" label="Удалить" @click="deleteBook"></Button>
    </div>
  </Dialog>

</template>

<script lang="ts">
import {AxiosResponse} from "axios";
import {defineComponent} from 'vue'
import {mapState} from "vuex";

import CreateComment from "@/components/CreateComment.vue";
import Bookmarks from "@/components/Bookmarks.vue";
import Comment from "@/components/Comment.vue";

import api from "@/services/api";
import {BookDetail} from "@/books";
import {CommentResult} from "@/comment"
import {getLanguagePairByLabel} from "@/languages";
import {formatBytes, textToHtml, wrapLinks} from "../formatter";
import BookViewStats from "@/components/BookViewStats.vue";

export default defineComponent({
  name: "BookPage",
  components: {BookViewStats, Bookmarks, Comment, CreateComment},
  data() {
    return {
      book: null as BookDetail | null,
      results: null as CommentResult | null,
      displayDeleteBookDialog: false,
    }
  },
  mounted() {
    this.getBook();
    this.getComments(1);
  },
  computed: {
    ...mapState({
      loggedIn: (state: any) => state.auth.status.loggedIn,
      user: (state: any) => state.auth.user,
    }),

    canCreateComment() {
      return this.loggedIn && this.user?.isStaff;
    },
    bookIdParam() {
      return this.$route.params.id
    }
  },
  methods: {
    wrapLinks,
    textToHtml,
    getLanguagePairByLabel,
    formatBytes,
    getBook() {
      if (this.book) return;
      api.get(`/books/${this.bookIdParam}`)
          .then(
              (value: AxiosResponse<BookDetail>) => {
                this.book = value.data;
                document.title = this.book.title;
              }
          )
    },
    getComments(page: number) {
      let url = `/comments/book/${this.bookIdParam}?page=${page}`
      if (this.results?.perPage) url += `&per-page=${this.results.perPage}`
      api.get(url).then(
          (value: AxiosResponse<CommentResult>) => this.results = value.data
      )
    },

    showEditBook() {
      document.location.href = `/book/${this.bookIdParam}/edit`;
    },

    deleteBook() {
      api.delete(`/books/${this.bookIdParam}`)
          .then(
              (value: AxiosResponse) => {
                if (value.status == 204) document.location.href = "/";
              }
          )
    },
    downloadBook() {
      if (this.book) document.location.href = '/api/v1/books/' + this.book.id + '/download?as-file=true'
    }
  }
})
</script>
