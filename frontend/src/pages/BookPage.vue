<template>
  <Menu/>

  <div v-if="book" class="flex flex-wrap justify-content-center align-items-center my-4">
    <a :href="'/book/'+book.id+'/show'" target="_blank" class="flex flex-column">
      <img style="width: 100%" class="border-round-xl" alt="book" :src="book.previewImage"/>
    </a>

    <div class="flex flex-column m-3 w-full" style="max-width: 40rem;">
      <h2 class="p-2">{{book.title}}</h2>

      <div class="pl-2 mb-3 flex flex-wrap align-items-center">
        <template v-if="loggedIn && user">
          <Bookmarks type="favorite" :bookId="book.id" :mark="book.favorite" @updated="v => book!.favorite = v" />
          <Bookmarks type="read" :bookId="book.id" :mark="book.read" @updated="v => book!.read = v" />
        </template>

        <template v-if="loggedIn && user && user.id == book.userId">
          <Button @click="showEditBook" v-tooltip.bottom="'Редактировать'" icon="pi pi-pencil" raised rounded outlined severity="warning" class="mx-1"/>
          <Button @click="displayDeleteBookDialog = true" v-tooltip.bottom="'Удалить'" icon="pi pi-trash" raised rounded outlined severity="danger" class="mx-1"/>
        </template>
      </div>

      <div class="p-2 pb-4">
        <BookViewStats :book="book" />
      </div>

      <div class="m-2">
        <span>Издательство <i class="pi pi-building mr-2"/></span>
        <a :href="'/?publisher='+book.publisher.name" class="text-primary no-underline" v-tooltip.bottom="'Фильтр по издателю'">{{book.publisher.name}}</a>
        <span class="ml-2" v-tooltip="'Год публикации оригинала'">{{book.year}} г.</span>
      </div>
      <div class="m-2">
        <span>Язык книги: {{book.language}}</span>
        <img :alt="book.language" :src="`https://flagcdn.com/${getLanguagePairByLabel(book.language).code}.svg`" class="ml-1 border-1 border-500" style="width: 18px" />
      </div>
      <div class="m-2">
        <i class="pi pi-users"/> {{book.authors}}
      </div>
      <div class="m-2">
        <i class="pi pi-book"/> {{book.pages}} стр.
        <i class="pi pi-file mx-2"/>{{formatBytes(book.size)}}
        <span @click="downloadBook" class="cursor-pointer hover:text-purple-400"><i class="pi pi-download mx-2"/>Загрузить</span>
      </div>
      <div class="m-2 chips">
        <a :href="'/?tags='+tag.name" v-for="(tag, index) in book.tags" >
          <Chip v-tooltip.bottom="'Найти похожие'" class="m-1" icon="pi pi-tag" :key="index" :label="tag.name" />
        </a>
      </div>
      <div class="p-3 w-full text-justify" v-html="textToHtml(book.description)"></div>
    </div>
  </div>

  <div v-if="book?.id && canCreateComment" class="flex justify-content-center">
    <CreateComment @created="getComments(1)" :book-id="book.id"/>
  </div>

  <div class="flex flex-wrap flex-column align-items-center" v-if="results">
    <Comment @comment:delete="getComments(1)" @comment:update="getComments(1)" v-for="(comment, index) in results.comments" :key="index" :comment="comment" />
    <Paginator class="w-full" v-if="results"
               :always-show="false"
               @page="(event: any) => getComments(event.page+1)"
               @update:rows="(value: number) => results!.perPage = value"
               v-model="results.currentPage"
               :rows="results.perPage" :totalRecords="results.totalCount" :rowsPerPageOptions="[10, 25, 50]" />
  </div>

  <Dialog v-model:visible="displayDeleteBookDialog" class="pt-2" :show-header="false" modal :style="{ width: '25rem' }">
    <div class="flex align-items-center py-4">
      <i class="text-5xl pi pi-exclamation-circle mr-2" />
      <h3>Вы уверены, что хотите удалить эту книгу?</h3>
    </div>

    <div class="flex justify-content-end gap-2">
      <Button type="button" severity="secondary" label="Остаться" @click="displayDeleteBookDialog = false"></Button>
      <Button type="button" severity="danger" label="Выйти" @click="deleteBook"></Button>
    </div>
  </Dialog>

  <Footer/>

</template>

<script lang="ts">
import {AxiosResponse} from "axios";
import {defineComponent} from 'vue'
import {mapState} from "vuex";

import CreateComment from "@/components/CreateComment.vue";
import Bookmarks from "@/components/Bookmarks.vue";
import Comment from "@/components/Comment.vue";
import Footer from "@/components/Footer.vue";
import Menu from "@/components/Menu.vue";

import api from "@/services/api";
import {BookDetail} from "@/books";
import {CommentResult} from "@/comment"
import {getLanguagePairByLabel} from "@/languages";
import {formatBytes, textToHtml} from "../formatter";
import BookViewStats from "@/components/BookViewStats.vue";

export default defineComponent({
  name: "BookPage",
  components: {BookViewStats, Bookmarks, Footer, Comment, CreateComment, Menu,},
  data() {
      return {
        book: null as BookDetail|null,
        results: null as CommentResult|null,
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
      if (this.book) document.location.href = '/api/v1/books/'+this.book.id+'/download?as-file=true'
    }
  }
})
</script>

<style scoped>

</style>